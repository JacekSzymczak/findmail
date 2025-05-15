import random
import string


class MailboxService:
    @staticmethod
    def get_or_create(name, user):
        """Get or create a mailbox name (which is actually a recipient address)."""
        try:
            # For catch-all, we just need to validate the mailbox name format
            # and construct the full email address
            mailbox_email = f"{name}@findmail.pl"
            return {"name": name, "email": mailbox_email, "user_id": user.id}
        except Exception as e:
            raise Exception(f"Error processing mailbox: {str(e)}")

    @staticmethod
    def generate_random(user):
        """Generate a new random mailbox name."""
        rand_name = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        return MailboxService.get_or_create(rand_name, user)
