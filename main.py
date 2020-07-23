import requests
from selenium import webdriver
import time
from dataclasses import dataclass
import pandas as pd

wait_time = 2


@dataclass
class ContestInfo:
    handle: str
    name = str
    contest_name = str
    solved = int = 0

    def __init__(self, handle, name, contest_name, solved):
        self.handle = handle
        self.name = name
        self.contest_name = contest_name
        self.solved = solved


def parse_handle_name(txt):
    handle, name = 'not found', 'not found'
    if txt.find('(') != -1:
        name = txt[txt.find('(') + 1: txt.find(')')]
        handle = txt[0: txt.find('(')]
    else:
        handle = txt[0: len(txt)]
    return handle.strip(), name.strip()


def check_page_availability(contest_links):
    for link in contest_links:
        response = requests.get(link)
        if response.status_code != 200:
            print('Current Status: {}'.format(response.status_code))
            print('Link is Wrong or currently unavailable!!!')
            exit()


contests_list = set()
contestants_list = set()
full_name = {}
details = []


def navigate_to_rank_list(contest_links, count_up_solve=True):
    driver = webdriver.Chrome()
    for rank_page_url in contest_links:
        driver.get(rank_page_url)

        driver.find_element_by_xpath(
            '/html/body/div[1]/div[3]/ul/li[6]/div/button[1]'
        ).click()
        time.sleep(wait_time)

        if count_up_solve:
            driver.find_element_by_xpath(
                '/html/body/div[6]/div/div/div[2]/div/div[1]/div[4]/div/label[1]'
            ).click()
            time.sleep(wait_time)

        try:
            driver.find_element_by_xpath(
                '/html/body/div[6]/div/div/div[2]/div/div[3]/table/thead/tr/th[1]/input'
            ).click()
            print('Okay!!! Previous Contest History Found!!!')
            time.sleep(wait_time)
        except:
            print('Okay!!! No Previous Contest History Found!!!')

        try:
            driver.find_element_by_xpath(
                '/html/body/div[6]/div/div/div[2]/div/div[1]/div[2]/div/label[1]'
            ).click()
            time.sleep(wait_time)
        except:
            print('Error!!!! show all button not found!!!')

        driver.find_element_by_xpath(
            '/html/body/div[6]/div/div/div[1]/button/span'
        ).click()
        time.sleep(wait_time)

        driver.get(rank_page_url)
        table_rows = driver.find_elements_by_xpath(
            '/html/body/div[1]/div[3]/div[1]/div[4]/div/table[1]/tbody/tr'
        )

        contest_title = driver.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div[1]/div[2]/h3'
        )
        contest_name = contest_title.text
        if contest_name.find('(') != -1:
            contest_name = contest_name[0: contest_name.find('(')]
        contest_name = contest_name.strip()

        contests_list.add(contest_name)

        for row in table_rows:
            data = row.text.split('\n')
            handle, name = parse_handle_name(data[1])
            contestants_list.add(handle)
            full_name[handle] = name
            solved = data[2].split()[0]
            details.append(ContestInfo(handle, name, contest_name, int(solved.strip())))

    driver.quit()


def generate_rank_list():
    contest_wise_solved = {}
    for handle in contestants_list:
        contest_wise_solved[handle] = {}
        for contest in contests_list:
            for val in details:
                if handle == val.handle and contest == val.contest_name:
                    contest_wise_solved[handle][contest] = int(val.solved)

    rank_list = {'Handle': [], 'Name': []}
    for contest_name in contests_list:
        rank_list.update({contest_name: []})
    rank_list.update({'Total': []})

    for handle in contestants_list:
        rank_list['Handle'].append(handle)
        rank_list['Name'].append(full_name[handle])
        tot = 0
        for contest in contests_list:
            rank_list[contest].append(contest_wise_solved[handle].get(contest, 0))
            tot += contest_wise_solved[handle].get(contest, 0)
        rank_list['Total'].append(tot)

    df = pd.DataFrame(rank_list).sort_values(
        by=['Total', 'Handle'], ascending=[False, True]
    )
    df = df.reset_index(drop=True)
    df.index.name = 'Rank'
    df.index += 1
    print(df)
    df.to_csv('rank_list.csv')


def main():
    contest_links = set()
    with open('contest_ids.txt', 'r') as f:
        for link in f.readlines():
            contest_links.add(link)
    if len(contest_links) == 0:
        print('Warning!!! No Contest Links Provided!!!')
        exit()
    check_page_availability(contest_links)
    navigate_to_rank_list(contest_links, True)
    generate_rank_list()


if __name__ == '__main__':
    main()
