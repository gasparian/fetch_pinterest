from fetch_pinterest import *
import config

if __name__ == "__main__":

    get_search_result(config)

    getter = PinterestAPI(path=config.folderPath, access_token=config.accessToken)
    if config.boardId:
        getter.get_images_from_board(config.boardId)
    else:
        pins_list = [i[:-1] for i in open('./data/pins_list.txt', 'r').readlines()]
        getter.get_pins(pins_list)