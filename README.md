# BS-Monitor

Files required:

monitors.yml:

    ---
    graffiti:
      release_link: https://graffitilink.release.link.com/
      webhook: https://discord.com/api/webhooks/webhook_data
      delay: 5

Basic usage:

    from monitor.monitor import Monitor

    monitor = Monitor()
    monitor.run()