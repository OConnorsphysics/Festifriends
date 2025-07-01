from plyer import notification

def send_notification(title: str, message: str, timeout: int = 5):
    """
    Show a local notification using Plyer.
    """
    notification.notify(
        title=title,
        message=message,
        timeout=timeout  # in seconds
    )
