"""
Classroom-oriented seed command for the BottleCRM comprehension exercise.

This deliberately reuses BottleCRM's normal seed_data command, but fixes:
- a small dataset size
- a reproducible random seed
- a pedagogically useful lead-state distribution

Run on a fresh database:
    python manage.py seed_comprehension_data

Optional:
    python manage.py seed_comprehension_data --email student@example.com
"""

from common.management.commands.seed_data import Command as SeedDataCommand


class Command(SeedDataCommand):
    help = "Seed the small deterministic CRM dataset used for the comprehension exercise"

    LEAD_STATUSES = [
        "assigned",
        "assigned",
        "in process",
        "in process",
        "recycled",
        "converted",
    ]

    def add_arguments(self, parser):
        # Keep the normal --email and --password interface, but hide the many
        # dataset-size choices from the classroom command.
        parser.add_argument(
            "--email",
            type=str,
            default="student@example.com",
            help="Classroom login email (default: student@example.com)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="testpass123",
            help="Password for a newly created user (default: testpass123)",
        )

    def handle(self, *args, **options):
        # Supply the complete option dictionary expected by seed_data.Command.
        # Keeping these values here makes the classroom dataset explicit and
        # identical for every student.
        classroom_options = {
            **options,
            "orgs": 1,
            "users_per_org": 3,
            "leads": 6,
            "accounts": 3,
            "contacts": 4,
            "opportunities": 2,
            "cases": 2,
            "tasks": 3,
            "goals": 0,
            "teams": 2,
            "tags": 5,
            "currency": "USD",
            "country": "US",
            "products": 2,
            "invoices": 2,
            "estimates": 1,
            "recurring_invoices": 1,
            "invoice_templates": 1,
            "seed": 42,
            "clear": False,
            "no_input": True,
        }
        return super().handle(*args, **classroom_options)

    def create_leads(self, org, profiles, teams, tags, contacts, count):
        """
        Use BottleCRM's existing lead generator while controlling only the
        state sequence. This preserves the upstream names, companies,
        relationships, assignments, tags, and other generated attributes.
        """
        if count != len(self.LEAD_STATUSES):
            raise ValueError(
                f"Comprehension dataset expects exactly {len(self.LEAD_STATUSES)} leads"
            )

        statuses = iter(self.LEAD_STATUSES)
        original_weighted_choice = self._weighted_choice

        def classroom_weighted_choice(weights_dict):
            if weights_dict is self.LEAD_STATUS_WEIGHTS:
                return next(statuses)
            return original_weighted_choice(weights_dict)

        self._weighted_choice = classroom_weighted_choice
        try:
            return super().create_leads(
                org, profiles, teams, tags, contacts, count
            )
        finally:
            self._weighted_choice = original_weighted_choice
