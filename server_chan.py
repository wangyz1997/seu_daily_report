import requests

server_chan_url = 'http://sc.ftqq.com/{0}.send?text={1}&desp={2}/'


def server_chan_send(key, content, description):
    print(content, '\r\n', description)
    if len(key) <= 0:
        return None

    get_url = server_chan_url.format(key, content, description)
    return requests.get(get_url)
