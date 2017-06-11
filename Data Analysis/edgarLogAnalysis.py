import csv
import os
import zipfile
import pandas as pd
import numpy as np
import glob
import sys
import logging
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import time
import datetime


def summary(all_data):
    data = pd.DataFrame()
    data = all_data
    # summary = pd.DataFrame()
    logging.debug('In the function : summary')
    csvpath=str(os.getcwd())
    # add Timestamp for the analysis purpose
    data['Timestamp'] = data[['date', 'time']].astype(str).sum(axis=1)
    # Create a summary that groups ip by date
    summary1=data['ip'].groupby(data['date']).describe()
    summaryipdescribe = pd.DataFrame(summary1)
    s=summaryipdescribe.transpose()
    s.to_csv(csvpath+"/summaryipbydatedescribe.csv")
    # Create a summary that groups cik by accession number
    summary2 = data['extention'].groupby(data['cik']).describe()
    summarycikdescribe = pd.DataFrame(summary2)
    summarycikdescribe.to_csv(csvpath+"/summarycikbyextentiondescribe.csv")
    # get Top 10 count of all cik with their accession number
    data['COUNT'] = 1  # initially, set that counter to 1.
    group_data = data.groupby(['date', 'cik', 'accession'])['COUNT'].count()  # sum function
    rankedData=group_data.rank()
    summarygroup=pd.DataFrame(rankedData)
    summarygroup.to_csv(csvpath+"/Top10cik.csv")
    # For anomaly detection -check the length of cik
    data['cik'] = data['cik'].astype('str')
    data['cik_length'] = data['cik'].str.len()
    data[(data['cik_length'] > 10)]
    data['COUNT'] = 1
    datagroup=pd.DataFrame(data)
    datagroup.to_csv(csvpath+"/LengthOfCikForAnomalyDetection.csv")
    # Per code count
    status = data.groupby(['code']).count()  # sum function
    status['COUNT']
    summary=pd.DataFrame(status)
    summary.to_csv(csvpath+"/PercodeCount.csv")

def replace_missingValues(all_data):
    data = pd.DataFrame()
    logging.debug('In the function : replace_missingValues')
    all_data.loc[all_data['extention'] == '.txt', 'extention'] = all_data["accession"].map(str) + all_data["extention"]
    all_data['browser'] = all_data['browser'].fillna('win')
    all_data['size'] = all_data['size'].fillna(0)
    all_data['size'] = all_data['size'].astype('int64')
    all_data = pd.DataFrame(all_data.join(all_data.groupby('cik')['size'].mean(), on='cik', rsuffix='_newsize'))
    all_data['size_newsize'] = all_data['size_newsize'].fillna(0)
    all_data['size_newsize'] = all_data['size_newsize'].astype('int64')
    all_data.loc[all_data['size'] == 0, 'size'] = all_data.size_newsize
    del all_data['size_newsize']
    data = all_data
    return data


def change_dataTypes(all_data):
    new_data = pd.DataFrame()
    logging.debug('In the function : change_dataTypes')
    all_data['zone'] = all_data['zone'].astype('int64')
    all_data['cik'] = all_data['cik'].astype('int64')
    all_data['code'] = all_data['code'].astype('int64')
    all_data['idx'] = all_data['idx'].astype('int64')
    all_data['noagent'] = all_data['noagent'].astype('int64')
    all_data['norefer'] = all_data['norefer'].astype('int64')
    all_data['crawler'] = all_data['crawler'].astype('int64')
    all_data['find'] = all_data['find'].astype('int64')
    newdata = replace_missingValues(all_data)
    newdata.to_csv("merged.csv",encoding='utf-8')
    summary(newdata)
    return 0


def create_dataframe(path):
    logging.debug('In the function : create_dataframe')
    all_data = pd.DataFrame()
    for f in glob.glob(path + '/log*.csv'):
        df = pd.read_csv(f, parse_dates=[1])
        all_data = all_data.append(df, ignore_index=True)
    return all_data


def assure_path_exists(path):
    logging.debug('In a function : assure_path_exists')
    if not os.path.exists(path):
        os.makedirs(path)


def get_dataOnLocal(monthlistdata, year):
    logging.debug('In the function : get_dataOnLocal')
    df = pd.DataFrame()
    foldername = str(year)
    path = str(os.getcwd()) + "/" + foldername
    assure_path_exists(path)
    for month in monthlistdata:
        with urlopen(month) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(path)
    df = create_dataframe(path)
    change_dataTypes(df)
    return 0


def get_allmonth_data(linkhtml, year):
    logging.debug('In the function : get_allmonth_data')
    allzipfiles = BeautifulSoup(linkhtml, "html.parser")
    ziplist = allzipfiles.find_all('li')
    monthlistdata = []
    count = 0
    for li in ziplist:
        zipatags = li.findAll('a')
        for zipa in zipatags:
            if "01.zip" in zipa.text:
                monthlistdata.append(zipa.get('href'))
    get_dataOnLocal(monthlistdata, year)


def get_url(year):
    logging.debug('In the function : get_url')
    url = 'https://www.sec.gov/data/edgar-log-file-data-set.html'
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    all_div = soup.findAll("div", attrs={'id': 'asyncAccordion'})
    for div in all_div:
        h2tag = div.findAll("a")
        for a in h2tag:
            if str(year) in a.get('href'):
                global ahref
                ahref = a.get('href')
    linkurl = 'https://www.sec.gov' + ahref
    logging.debug('Calling the initial URL')
    linkhtml = urlopen(linkurl)
    get_allmonth_data(linkhtml, year)


def valid_year(year):
    logging.debug('In the function : valid_year')
    logYear = ['2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015',
               '2016']
    for log in logYear:
        try:
            if year in log:
                get_url(year)
        except:
            print("Data for" + year + "does not exist")
            "Data for" + year + "does not exist"


def main():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
    args = sys.argv[1:]

    year = ''
    counter = 0
    if len(args) == 0:
        year = "2003"
    for arg in args:
        if counter == 0:
            year= str(arg)
        counter += 1
    logfilename = 'log_Edgar_'+ year + '_' + st + '.txt'
    logging.basicConfig(filename=logfilename, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Program Start')
    logging.debug('*************')    
    logging.debug('Calling the initial URL'.format(year))
    valid_year(year)


if __name__ == '__main__':
    main()

