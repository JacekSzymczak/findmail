import random
import string


class MailboxService:
    @staticmethod
    def get_or_create(name, user):
        """Retrieve an existing mailbox or create a new one."""
        # TODO: Implement direct IMAP connection
        return {"name": name, "user_id": user.id}

    @staticmethod
    def generate_random(user):
        """Generate a new random mailbox name."""
        rand_name = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        return {"name": rand_name, "user_id": user.id}
