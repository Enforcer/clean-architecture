def async_handler_generic_task(cls, *args, **kwargs):  # type: ignore
    """
    This function is meant to be used for running asynchronous event handlers.

    It bootstraps application context and wraps task with DB transaction.
    """
    from main import bootstrap_app

    app = bootstrap_app()
    with app.connection_provider.open():
        instance = app.injector.create_object(cls)
        instance(*args, **kwargs)
