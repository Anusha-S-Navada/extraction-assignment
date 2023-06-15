import os




def removeFile(path,logger):
    try:
        os.remove(path)
        logger.info("Sucessfully deleted the file:{}".format(path))
    except Exception as e:
        logger.error("Exception in deleting the file:{}".format(repr(e)))