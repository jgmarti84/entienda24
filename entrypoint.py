from app import app


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(
        debug=True,
        host="localhost",
        port=8001,
        # ssl_context='adhoc'
    )