from waybackpy import WaybackMachineCDXServerAPI, WaybackMachineSaveAPI

user_agent = "savemypage aplication"


def _get_existing_archive(url):
    cdx_api = WaybackMachineCDXServerAPI(url, user_agent)
    return cdx_api.newest().archive_url


def _archive_url(url):
    save_api = WaybackMachineSaveAPI(url, user_agent)
    return save_api.save()


def get_url_archive(url):
    try:
        # return existing url if it exists
        return _get_existing_archive(url)
    except Exception as ex:
        print(ex)
        # save link if it does not exist
        return _archive_url(url)


# call and insert archive
def archive(url, db):
    try:
        archive_url = get_url_archive(url)
        url_records = db.fetch({"url": url})
        keys = [item["key"] for item in url_records.items]
        for key in keys:
            db.update({"archive_url": archive_url}, key)
    except Exception as ex:
        print(ex)
