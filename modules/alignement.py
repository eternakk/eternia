from modules.logging_config import get_logger

class AlignmentGovernor:
    def __init__(self, core_rules=None):
        # List of rules or constraints (functions or objects)
        self.core_rules = core_rules or [self.prevent_harm, self.maintain_user_agency]
        self.logger = get_logger("alignment")

    def check_action(self, action_context):
        """
        Evaluate proposed action in the current context.
        Returns True if the action passes alignment checks.
        """
        for rule in self.core_rules:
            if not rule(action_context):
                self.logger.warning(f"🚨 AlignmentGovernor: Action blocked by rule: {rule.__name__}")
                return False
        return True

    def prevent_harm(self, action_context):
        # Example rule: No physical/psychological harm allowed
        return not action_context.get("causes_harm", False)

    def maintain_user_agency(self, action_context):
        # Example rule: Never override user free will
        return not action_context.get("removes_agency", False)

    # Add more rules as needed!
