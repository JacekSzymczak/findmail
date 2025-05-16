import base64
import email
import imaplib
import re
from datetime import datetime
from email.header import decode_header

from flask import current_app


class MessageService:
    @staticmethod
    def _make_message_id_safe(message_id: str) -> str:
        """
        Convert Message-ID to URL-safe Base64 (no padding).
        E.g. '<1234@domain>' → 'PDEyMzRAZG9tYWluPg'
        """
        try:
            raw = message_id.encode("utf-8")
            b64 = base64.urlsafe_b64encode(raw).rstrip(b"=")
            return b64.decode("ascii")
        except Exception as e:
            current_app.logger.error(f"Error encoding message ID: {e}")
            raise ValueError(f"Invalid message ID format: {e}")

    @staticmethod
    def _make_message_id_full(safe_id: str) -> str:
        """
        Convert URL-safe Base64 back to original Message-ID.
        E.g. 'PDEyMzRAZG9tYWluPg' → '<1234@domain>'
        """
        try:
            b64 = safe_id.encode("ascii")
            # restore padding
            padding = b"=" * (-len(b64) % 4)
            raw = base64.urlsafe_b64decode(b64 + padding)
            return raw.decode("utf-8")
        except Exception as e:
            current_app.logger.error(f"Error decoding message ID: {e}")
            raise ValueError(f"Invalid safe message ID format: {e}")

    @staticmethod
    def list_messages(mailbox_name: str):
        """List last 10 messages in INBOX for mailbox_name."""
        try:
            imap = imaplib.IMAP4_SSL(
                current_app.config["IMAP_HOST"], current_app.config["IMAP_PORT"]
            )
            imap.login(
                current_app.config["IMAP_USER"], current_app.config["IMAP_PASSWORD"]
            )
            imap.select("INBOX")

            recipient = f"{mailbox_name}@findmail.pl"
            _, nums = imap.search(None, f'TO "{recipient}"')

            msgs = []
            for num in reversed(nums[0].split()[-10:]):
                _, data = imap.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                # use actual Message-ID header if present
                orig_id = msg.get("Message-ID", f"<{num.decode()}>")
                safe_id = MessageService._make_message_id_safe(orig_id)

                # decode subject
                subject = ""
                for part, enc in decode_header(msg.get("Subject", "")):
                    if isinstance(part, bytes):
                        subject += part.decode(enc or "utf-8", errors="replace")
                    else:
                        subject += part

                # get plain-text and HTML body
                body = ""
                html_body = ""
                embedded_images = {}  # Store CID -> base64 image mappings

                if msg.is_multipart():
                    # First pass: collect all embedded images
                    for p in msg.walk():
                        if p.get_content_maintype() == "image":
                            content_id = p.get("Content-ID", "").strip("<>")
                            if content_id:
                                try:
                                    image_data = p.get_payload(decode=True)
                                    if image_data:
                                        # Convert to base64 for embedding
                                        image_b64 = base64.b64encode(image_data).decode(
                                            "ascii"
                                        )
                                        embedded_images[content_id] = {
                                            "data": f"data:{p.get_content_type()};base64,{image_b64}",
                                            "content_type": p.get_content_type(),
                                        }
                                except Exception as e:
                                    current_app.logger.warning(
                                        f"Error processing embedded image: {e}"
                                    )

                    # Second pass: process text content
                    for p in msg.walk():
                        content_type = p.get_content_type()
                        if content_type == "text/plain":
                            try:
                                body = p.get_payload(decode=True).decode(
                                    p.get_content_charset() or "utf-8", errors="replace"
                                )
                            except Exception as e:
                                current_app.logger.warning(
                                    f"Error decoding plain text body part: {e}"
                                )
                                body = "Error decoding content"
                        elif content_type == "text/html":
                            try:
                                html_body = p.get_payload(decode=True).decode(
                                    p.get_content_charset() or "utf-8", errors="replace"
                                )
                            except Exception as e:
                                current_app.logger.warning(
                                    f"Error decoding HTML body part: {e}"
                                )
                                html_body = "Error decoding content"
                else:
                    content_type = msg.get_content_type()
                    try:
                        if content_type == "text/html":
                            html_body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="replace"
                            )
                        else:
                            body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="replace"
                            )
                    except Exception as e:
                        current_app.logger.warning(f"Error decoding body: {e}")
                        if content_type == "text/html":
                            html_body = "Error decoding content"
                        else:
                            body = "Error decoding content"

                # Parse date with error handling
                received_at = None
                try:
                    date_str = msg.get("Date")
                    if date_str:
                        received_at = datetime.strptime(
                            date_str, "%a, %d %b %Y %H:%M:%S %z"
                        )
                except Exception as e:
                    current_app.logger.warning(f"Error parsing date: {e}")

                msgs.append(
                    {
                        "id": safe_id,
                        "imap_id": num.decode(),
                        "received_at": received_at,
                        "sender": msg.get("From"),
                        "subject": subject,
                        "body": body,
                        "html_body": html_body,
                        "is_html": bool(html_body),
                        "embedded_images": embedded_images,
                    }
                )

            imap.close()
            imap.logout()
            return msgs

        except Exception as e:
            raise Exception(f"Error listing messages: {e}")

    @staticmethod
    def get_message(mailbox_name: str, safe_message_id: str):
        """Retrieve a single message by its URL-safe Base64 ID."""
        try:
            imap = imaplib.IMAP4_SSL(
                current_app.config["IMAP_HOST"], current_app.config["IMAP_PORT"]
            )
            imap.login(
                current_app.config["IMAP_USER"], current_app.config["IMAP_PASSWORD"]
            )
            imap.select("INBOX")

            try:
                full_id = MessageService._make_message_id_full(safe_message_id)
                current_app.logger.info(f"Decoded message ID: {full_id}")
            except ValueError as e:
                current_app.logger.error(f"Invalid message ID format: {e}")
                return None

            # First try to find by Message-ID
            current_app.logger.info(f"Searching for message with ID: {full_id}")
            _, nums = imap.search(None, f'HEADER Message-ID "{full_id}"')
            current_app.logger.info(
                f"Search results: {nums[0] if nums[0] else 'No results'}"
            )

            if not nums[0]:
                # If not found by Message-ID, try to find by sequence number
                current_app.logger.info(
                    f"Message not found by ID, trying sequence number: {safe_message_id}"
                )
                try:
                    # Convert the safe_message_id to a sequence number if it's numeric
                    if safe_message_id.isdigit():
                        num = safe_message_id
                    else:
                        # Try to find the message by its original ID
                        _, nums = imap.search(
                            None, f'HEADER Message-ID "{safe_message_id}"'
                        )
                        if not nums[0]:
                            current_app.logger.warning(
                                "Message not found by ID or sequence number"
                            )
                            return None
                        num = nums[0].split()[0]

                    current_app.logger.info(f"Using sequence number: {num}")
                    _, data = imap.fetch(num, "(RFC822)")
                    if not data or not data[0]:
                        current_app.logger.warning(
                            f"No data returned for sequence number {num}"
                        )
                        return None
                except Exception as e:
                    current_app.logger.error(f"Error fetching by sequence number: {e}")
                    return None
            else:
                num = nums[0].split()[0]
                current_app.logger.info(f"Found message with sequence number: {num}")
                _, data = imap.fetch(num, "(RFC822)")
                if not data or not data[0]:
                    current_app.logger.warning(
                        f"No data returned for sequence number {num}"
                    )
                    return None

            msg = email.message_from_bytes(data[0][1])
            current_app.logger.info(f"Message headers: {dict(msg.items())}")

            # confirm it's for this mailbox
            recipient = f"{mailbox_name}@findmail.pl"
            to_headers = msg.get_all("To", [])
            current_app.logger.info(f"Message To headers: {to_headers}")

            # Check if recipient is in any of the To headers
            recipient_found = False
            for to_header in to_headers:
                # Extract email from formats like:
                # "test@findmail.pl" <test@findmail.pl>
                # test@findmail.pl
                # <test@findmail.pl>
                email_match = re.search(r'<?([^<>"\s]+@[^<>"\s]+)>?', to_header)
                if email_match and email_match.group(1).lower() == recipient.lower():
                    recipient_found = True
                    break

            if not recipient_found:
                current_app.logger.warning(f"Message not for recipient {recipient}")
                return None

            # decode fields (same as list_messages)
            subject = ""
            for part, enc in decode_header(msg.get("Subject", "")):
                if isinstance(part, bytes):
                    subject += part.decode(enc or "utf-8", errors="replace")
                else:
                    subject += part

            body = ""
            html_body = ""
            if msg.is_multipart():
                for p in msg.walk():
                    content_type = p.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = p.get_payload(decode=True).decode(
                                p.get_content_charset() or "utf-8", errors="replace"
                            )
                        except Exception as e:
                            current_app.logger.warning(
                                f"Error decoding plain text body part: {e}"
                            )
                            body = "Error decoding content"
                    elif content_type == "text/html":
                        try:
                            html_body = p.get_payload(decode=True).decode(
                                p.get_content_charset() or "utf-8", errors="replace"
                            )
                        except Exception as e:
                            current_app.logger.warning(
                                f"Error decoding HTML body part: {e}"
                            )
                            html_body = "Error decoding content"
            else:
                content_type = msg.get_content_type()
                try:
                    if content_type == "text/html":
                        html_body = msg.get_payload(decode=True).decode(
                            msg.get_content_charset() or "utf-8", errors="replace"
                        )
                    else:
                        body = msg.get_payload(decode=True).decode(
                            msg.get_content_charset() or "utf-8", errors="replace"
                        )
                except Exception as e:
                    current_app.logger.warning(f"Error decoding body: {e}")
                    if content_type == "text/html":
                        html_body = "Error decoding content"
                    else:
                        body = "Error decoding content"

            # Parse date with error handling
            received_at = None
            try:
                date_str = msg.get("Date")
                if date_str:
                    received_at = datetime.strptime(
                        date_str, "%a, %d %b %Y %H:%M:%S %z"
                    )
            except Exception as e:
                current_app.logger.warning(f"Error parsing date: {e}")

            result = {
                "id": safe_message_id,
                "imap_id": num.decode(),
                "received_at": received_at,
                "sender": msg.get("From"),
                "subject": subject,
                "body": body,
                "html_body": html_body,
                "is_html": bool(html_body),
            }

            imap.close()
            imap.logout()
            return result

        except Exception as e:
            current_app.logger.error(f"Error retrieving message: {e}", exc_info=True)
            raise Exception(f"Error retrieving message: {e}")

    @staticmethod
    def delete_message(mailbox_name: str, safe_message_id: str) -> bool:
        """Permanently delete a message by its URL-safe Base64 ID."""
        try:
            imap = imaplib.IMAP4_SSL(
                current_app.config["IMAP_HOST"], current_app.config["IMAP_PORT"]
            )
            imap.login(
                current_app.config["IMAP_USER"], current_app.config["IMAP_PASSWORD"]
            )
            imap.select("INBOX")

            try:
                full_id = MessageService._make_message_id_full(safe_message_id)
                current_app.logger.info(f"Decoded message ID for deletion: {full_id}")
            except ValueError as e:
                current_app.logger.error(f"Invalid message ID format for deletion: {e}")
                return False

            # First try to find by Message-ID
            current_app.logger.info(
                f"Searching for message to delete with ID: {full_id}"
            )
            _, nums = imap.search(None, f'HEADER Message-ID "{full_id}"')
            current_app.logger.info(
                f"Search results for deletion: {nums[0] if nums[0] else 'No results'}"
            )

            if not nums[0]:
                # If not found by Message-ID, try to find by sequence number
                current_app.logger.info(
                    f"Message not found by ID for deletion, trying sequence number: {safe_message_id}"
                )
                try:
                    # Convert the safe_message_id to a sequence number if it's numeric
                    if safe_message_id.isdigit():
                        num = safe_message_id
                    else:
                        current_app.logger.warning(
                            "Message not found by ID or sequence number for deletion"
                        )
                        return False

                    current_app.logger.info(
                        f"Using sequence number for deletion: {num}"
                    )
                except Exception as e:
                    current_app.logger.error(
                        f"Error processing sequence number for deletion: {e}"
                    )
                    return False
            else:
                num = nums[0].split()[0]
                current_app.logger.info(
                    f"Found message for deletion with sequence number: {num}"
                )

            # Verify the message is for this mailbox before deleting
            _, data = imap.fetch(num, "(RFC822)")
            if not data or not data[0]:
                current_app.logger.warning(
                    f"No data returned for sequence number {num} during deletion"
                )
                return False

            msg = email.message_from_bytes(data[0][1])
            recipient = f"{mailbox_name}@findmail.pl"
            to_headers = msg.get_all("To", [])
            current_app.logger.info(f"Message To headers for deletion: {to_headers}")

            # Check if recipient is in any of the To headers
            recipient_found = False
            for to_header in to_headers:
                email_match = re.search(r'<?([^<>"\s]+@[^<>"\s]+)>?', to_header)
                if email_match and email_match.group(1).lower() == recipient.lower():
                    recipient_found = True
                    break

            if not recipient_found:
                current_app.logger.warning(
                    f"Message not for recipient {recipient} during deletion"
                )
                return False

            # Delete the message
            current_app.logger.info(f"Marking message {num} for deletion")
            imap.store(num, "+FLAGS", "\\Deleted")
            imap.expunge()
            current_app.logger.info(f"Message {num} successfully deleted")

            imap.close()
            imap.logout()
            return True

        except Exception as e:
            current_app.logger.error(f"Error deleting message: {e}", exc_info=True)
            raise Exception(f"Error deleting message: {e}")
