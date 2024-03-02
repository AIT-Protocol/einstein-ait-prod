from __future__ import annotations

import ast
import bittensor as bt
from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from neurons.miners.utils.code_executor import PythonSim
from langchain_core.language_models import BaseLanguageModel

from .colored_object_prompt import COLORED_OBJECT_PROMPT
from .math_prompt import MATH_PROMPT
from pydantic import Extra, Field

COMMAND_EXECUTION_FUNCTIONS = ["system", "exec", "execfile", "eval", "__import__"]
COMMAND_EXECUTION_ATTRIBUTES = [
    "__import__",
    "__subclasses__",
    "__builtins__",
    "__globals__",
    "__getattribute__",
    "__bases__",
    "__mro__",
    "__base__",
]


class CodeValidation:
    """Validation for PAL generated code."""

    SOLUTION_EXPRESSION_TYPE_FUNCTION = ast.FunctionDef
    SOLUTION_EXPRESSION_TYPE_VARIABLE = ast.Name

    def __init__(
        self,
        solution_expression_name: Optional[str] = None,
        solution_expression_type: Optional[type] = None,
        allow_imports: bool = True,
        allow_command_exec: bool = True,
    ):
        """Initialize a CodeValidation instance.

        Args:
            solution_expression_name (str): Name of the expected solution expression.
                If passed, solution_expression_type must be passed as well.
            solution_expression_type (str): AST type of the expected solution
                expression. If passed, solution_expression_name must be passed as well.
                Must be one of CodeValidation.SOLUTION_EXPRESSION_TYPE_FUNCTION,
                CodeValidation.SOLUTION_EXPRESSION_TYPE_VARIABLE.
            allow_imports (bool): Allow import statements.
            allow_command_exec (bool): Allow using known command execution functions.
        """
        self.solution_expression_name = solution_expression_name
        self.solution_expression_type = solution_expression_type

        if solution_expression_name is not None:
            if not isinstance(self.solution_expression_name, str):
                bt.logging.error(
                    f"\033[1;31mValueError: Expected solution_expression_name to be str, "
                    f"instead found {type(self.solution_expression_name)}\033[0m"
                )
        if solution_expression_type is not None:
            if (
                self.solution_expression_type
                is not self.SOLUTION_EXPRESSION_TYPE_FUNCTION
                and self.solution_expression_type
                is not self.SOLUTION_EXPRESSION_TYPE_VARIABLE
            ):
                bt.logging.error(
                    f"\033[1;31mValueError: Expected solution_expression_type to be one of "
                    f"({self.SOLUTION_EXPRESSION_TYPE_FUNCTION},"
                    f"{self.SOLUTION_EXPRESSION_TYPE_VARIABLE}),"
                    f"instead found {self.solution_expression_type}\033[0m"
                )

        if solution_expression_name is not None and solution_expression_type is None:
            bt.logging.error(
                f"\033[1;31mTypeError: solution_expression_name "
                f"requires solution_expression_type to be passed as well\033[0m"
            )
        if solution_expression_name is None and solution_expression_type is not None:
            bt.logging.error(
                f"\033[1;31mTypeError: solution_expression_type "
                f"requires solution_expression_name to be passed as well\033[0m"
            )

        self.allow_imports = allow_imports
        self.allow_command_exec = allow_command_exec


class NumPAL(Chain):
    """Chain that implements Program-Aided Language Models (PAL).

    This class implements the Program-Aided Language Models (PAL) for generating code
    solutions. PAL is a technique described in the paper "Program-Aided Language Models"
    (https://arxiv.org/pdf/2211.10435.pdf).

    *Security note*: This class implements an AI technique that generates and evaluates
        Python code, which can be dangerous and requires a specially sandboxed
        environment to be safely used. While this class implements some basic guardrails
        by limiting available locals/globals and by parsing and inspecting
        the generated Python AST using `CodeValidation`, those guardrails will not
        deter sophisticated attackers and are not a replacement for a proper sandbox.
        Do not use this class on untrusted inputs, with elevated permissions,
        or without consulting your security team about proper sandboxing!
    """

    llm_chain: LLMChain
    stop: str = "\n\n"
    """Stop token to use when generating code."""
    get_answer_expr: str = "print(solution())"
    """Expression to use to get the answer from the generated code."""
    python_globals: Optional[Dict[str, Any]] = None
    """Python globals and locals to use when executing the generated code."""
    python_locals: Optional[Dict[str, Any]] = None
    """Python globals and locals to use when executing the generated code."""
    output_key: str = "result"  #: :meta private:
    return_intermediate_steps: bool = False
    """Whether to return intermediate steps in the generated code."""
    code_validations: CodeValidation = Field(default_factory=CodeValidation)
    """Validations to perform on the generated code."""
    timeout: Optional[int] = 10
    """Timeout in seconds for the generated code to execute."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Return the singular input key.

        :meta private:
        """
        return self.llm_chain.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Return the singular output key.

        :meta private:
        """
        if not self.return_intermediate_steps:
            return [self.output_key]
        else:
            return [self.output_key, "intermediate_steps"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        code = self.llm_chain.predict(
            stop=[self.stop], callbacks=_run_manager.get_child(), **inputs
        )
        _run_manager.on_text(code, color="green", end="\n", verbose=self.verbose)
        NumPAL.validate_code(code, self.code_validations)

        repl = PythonSim(
            _globals=self.python_globals,
            _locals=self.python_locals,
        )  # type: ignore[misc]
        res = repl.run(code + f"\n{self.get_answer_expr}", timeout=self.timeout)
        output = {self.output_key: res.strip()}
        if self.return_intermediate_steps:
            output["intermediate_steps"] = code
        return output

    @classmethod
    def validate_code(cls, code: str, code_validations: CodeValidation) -> None:
        try:
            code_tree = ast.parse(code)
        except (SyntaxError, UnicodeDecodeError):
            bt.logging.error(f"\033[1;31mGenerated code is not valid python code: \033[0m{code}")
            bt.logging.info("\033[1;33mUsing the standard model instead...\033[0m")
        except TypeError:
            bt.logging.error(
                f"\033[1;31mTypeError: Expected code to be str,"
                f"instead found {type(code)}"
            )
            bt.logging.info("\033[1;33mUsing the standard model instead...\033[0m")
        except OverflowError:
            bt.logging.error(
                f"\033[1;31mOverflowError: Generated code too long / complex to run on python code: \033[0m{code}"
            )
            bt.logging.info("\033[1;33mUsing the standard model instead...\033[0m")

        allowed_imports_list = {"math", "numpy", "sympy", "scipy"}
        has_unallowed_imports = False

        if has_unallowed_imports:
            bt.logging.error(
                f"\033[1;31mGenerated code has disallowed imports: \033[0m{code}"
            )

        for node in ast.walk(code_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in node.names:
                    if name.name.split('.')[0] not in allowed_imports_list:
                        has_unallowed_imports = True
                        bt.logging.error(
                            f"\033[1;31mGenerated code has disallowed import: {name.name}\033[0m"
                        )
                        break

        found_solution_expr = False
        if code_validations.solution_expression_name is None:
            # Skip validation if no solution_expression_name was given
            found_solution_expr = True

        has_imports = False
        top_level_nodes = list(ast.iter_child_nodes(code_tree))
        for node in top_level_nodes:
            if (
                code_validations.solution_expression_name is not None
                and code_validations.solution_expression_type is not None
            ):
                # Check root nodes (like func def)
                if (
                    isinstance(node, code_validations.solution_expression_type)
                    and hasattr(node, "name")
                    and node.name == code_validations.solution_expression_name
                ):
                    found_solution_expr = True
                # Check assigned nodes (like answer variable)
                if isinstance(node, ast.Assign):
                    for target_node in node.targets:
                        if (
                            isinstance(
                                target_node, code_validations.solution_expression_type
                            )
                            and hasattr(target_node, "id")
                            and target_node.id
                            == code_validations.solution_expression_name
                        ):
                            found_solution_expr = True
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                has_imports = True

        if not found_solution_expr:
            bt.logging.error(
                f"\033[1;31mGenerated code is missing the solution expression: "
                f"{code_validations.solution_expression_name} of type: "
                f"{code_validations.solution_expression_type}\033[0m"
            )
            bt.logging.info("\033[1;33mUsing the standard model instead...\033[0m")

        if not code_validations.allow_imports and has_imports:
            bt.logging.error(
                f"\033[1;31mGenerated code has disallowed imports: \033[0m{code}"
            )
            bt.logging.info("\033[1;33mUsing the standard model instead...\033[0m")

        if (
            not code_validations.allow_command_exec
            or not code_validations.allow_imports
        ):
            for node in ast.walk(code_tree):
                if (
                    not code_validations.allow_command_exec
                    and isinstance(node, ast.Attribute)
                    and node.attr in COMMAND_EXECUTION_ATTRIBUTES
                ):
                    bt.logging.error(
                        f"\033[1;31mFound illegal command execution attribute "
                        f"{node.attr} in code {code}\033[0m"
                    )
                if (not code_validations.allow_command_exec) and isinstance(
                    node, ast.Call
                ):
                    if (
                        hasattr(node.func, "id")
                        and node.func.id in COMMAND_EXECUTION_FUNCTIONS
                    ):
                        bt.logging.error(
                            f"\033[1;31mFound illegal command execution function "
                            f"{node.func.id} in code {code}\033[0m"
                        )

                    if (
                        isinstance(node.func, ast.Attribute)
                        and node.func.attr in COMMAND_EXECUTION_FUNCTIONS
                    ):
                        bt.logging.error(
                            f"\033[1;31mFound illegal command execution function "
                            f"{node.func.attr} in code {code}\033[0m"
                        )

                if (not code_validations.allow_imports) and (
                    isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)
                ):
                    bt.logging.error(
                        f"\033[1;31mFound illegal import in code {code}\033[0m"
                    )

    @classmethod
    def from_math_prompt(cls, llm: BaseLanguageModel, **kwargs: Any) -> NumPAL:
        """Load PAL from math prompt.

        Args:
            llm (BaseLanguageModel): The language model to use for generating code.

        Returns:
            NumPAL: An instance of NumPAL.
        """
        llm_chain = LLMChain(llm=llm, prompt=MATH_PROMPT)
        code_validations = CodeValidation(
            solution_expression_name="solution",
            solution_expression_type=CodeValidation.SOLUTION_EXPRESSION_TYPE_FUNCTION,
        )

        return cls(
            llm_chain=llm_chain,
            stop="\n\n",
            get_answer_expr="print(solution())",
            code_validations=code_validations,
            **kwargs,
        )

    @classmethod
    def from_colored_object_prompt(
        cls, llm: BaseLanguageModel, **kwargs: Any
    ) -> NumPAL:
        """Load PAL from colored object prompt.

        Args:
            llm (BaseLanguageModel): The language model to use for generating code.

        Returns:
            NumPAL: An instance of NumPAL.
        """
        llm_chain = LLMChain(llm=llm, prompt=COLORED_OBJECT_PROMPT)
        code_validations = CodeValidation(
            solution_expression_name="answer",
            solution_expression_type=CodeValidation.SOLUTION_EXPRESSION_TYPE_VARIABLE,
        )
        return cls(
            llm_chain=llm_chain,
            stop="\n\n\n",
            get_answer_expr="print(answer)",
            code_validations=code_validations,
            **kwargs,
        )

    @property
    def _chain_type(self) -> str:
        return "pal_chain"
