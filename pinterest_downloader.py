from fetch_pinterest import *
import config

if __name__ == "__main__":

    getter = PinterestAPI(path=config.folder_path, access_token=config.access_token, timeout=config.timeout)
    if config.board_ids:
        for board_id in config.board_ids:
            getter.get_images_from_board(board_id)
    else:
    	get_search_result(config)
        pins_list = [i[:-1] for i in open('./data/pins_list.txt', 'r').readlines()]
        getter.get_pins(pins_list)