import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from a11y_guardian.ir import ScreenSemanticTree
from a11y_guardian.agent.schemas import A11yAuditResult

class BaseA11yAuditor(ABC):
    """Base interface for all AI auditing engines."""

    def __init__(self, language: str = "kotlin"):
        base_dir = Path(__file__).resolve().parent.parent
        skills_dir = base_dir / "skills"
        rules_path = base_dir / "rules" / "wcag_2_2_mobile.md"

        compact_skill_filenames = {
            "kotlin": "compose_accessibility_skill_template.md",
            "swift": "swiftui_accessibility_skill_template.md",
        }
        skill_language = "swift" if language == "swift" else "kotlin"
        use_compact_skill = os.getenv("A11Y_USE_COMPACT_SKILL", "true").strip().lower()
        if use_compact_skill not in {"true", "false"}:
            raise ValueError("A11Y_USE_COMPACT_SKILL must be 'true' or 'false'.")

        if use_compact_skill == "true":
            skill_path = skills_dir / compact_skill_filenames[skill_language]
            if not skill_path.is_file():
                raise FileNotFoundError(f"Missing critical skill file: {skill_path}")
            skill_paths = [skill_path]
        else:
            language_dir = skills_dir / skill_language
            skill_paths = sorted(path for path in language_dir.glob("*/SKILL.md") if path.is_file())
            if not skill_paths:
                raise FileNotFoundError(f"No skill files found matching {language_dir / '*/SKILL.md'}")

        if not rules_path.is_file():
            raise FileNotFoundError(f"Missing WCAG rules file: {rules_path}")

        skill_content = "\n\n".join(
            re.sub(
                r"\A---[^\S\n]*\n.*?^---[^\S\n]*(?:\n|$)",
                "",
                path.read_text(encoding="utf-8"),
                flags=re.MULTILINE | re.DOTALL,
            ).strip()
            for path in skill_paths
        )
        wcag_content = f"\n\nLegal and technical reference framework:\n{rules_path.read_text(encoding='utf-8')}".strip()

        self.system_instruction = f"{skill_content}\n\n{wcag_content}".strip()

        # Optional: print the size for debug and confirmation
        print(f"[DEBUG BaseA11yAuditor] System Instructions loaded successfully ({len(self.system_instruction)} characters).")

    def build_user_prompt(self, tree: ScreenSemanticTree, distilled_code: str) -> str:
        """
        Build the user prompt in a generic way.
        Python only establishes the GitHub line replacement protocol.
        """
        code_fence = "```"
        return (
            f"Detected node structure (IR):\n"
            f"{code_fence}json\n"
            f"{tree.model_dump_json(exclude_none=True, indent=2)}\n"
            f"{code_fence}\n\n"
            f"Numbered relevant code:\n"
            f"{code_fence}text\n"
            f"{distilled_code}\n"
            f"{code_fence}\n\n"
            "GITHUB INLINE SUGGESTION MECHANICS:\n"
            "- Each item in 'suggestions' is anchored at 'line'.\n"
            "- GitHub will ONLY replace that line with the content of 'suggested_code'.\n"
            "- To avoid duplicating code, 'suggested_code' should not overwrite adjacent lines that must remain intact.\n\n"
            "Respond with strict JSON starting with '{' and ending with '}':\n"
            '{"suggestions": [{"line": <int>, "issue": "<string>", "suggested_code": "<string>"}]}'
        )

    @abstractmethod
    def audit_screen(self, tree: ScreenSemanticTree, distilled_code: str) -> A11yAuditResult:
        """Abstract method that each AI provider must implement."""
        pass
