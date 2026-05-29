class NotificationService:
    TEMPLATES = {
        "en": {
            "maintenance_reminder": "CleanFlow Reminder: It is time for a routine check of your water source '{source_name}'. Please ensure it remains Safe.",
        },
        "kri": {
            "maintenance_reminder": "CleanFlow Reminder: Time don reach for check your water source '{source_name}'. Abeg make sure say e de Safe.",
        }
    }

    def get_maintenance_reminder(self, source_name, language="en"):
        lang = language if language in self.TEMPLATES else "en"
        template = self.TEMPLATES[lang]["maintenance_reminder"]
        return template.format(source_name=source_name)
