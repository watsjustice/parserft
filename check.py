import json
import requests
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import csv
import pandas

def get_links(url , teamname):

	try:
		driver = webdriver.Chrome(
			executable_path = 'C:/Users/Денис/Desktop/Web/parser1/chromedriver.exe'		
		)

		driver.get(url)
		sleep(2)

		with open('selenium_links.html' , 'w' , encoding = 'utf-8') as f:
			f.write(driver.page_source)
		with open('selenium_links.html') as f:
			r = f.read()

		r = driver.page_source
		r = BeautifulSoup(r , 'lxml').find(id = 'teams')   								

		# сохраняем ссылку и название команды в словарь
		data_links = {}
		for item in r:
			data_links[item.text] = item.get('value')
		
		#мзабор ссылок на команды
		team_choice = driver.find_element_by_id('teams')
		team_choice = team_choice.find_elements_by_tag_name('option')

		for item in team_choice:

			if data_links[teamname] == item.get_attribute('value'):
				item.click()
				break


		sleep(5)    #даем время на подгрузку html кода

		#сохраняем html код
		with open('team.html' , 'w' , encoding = 'utf-8') as f:
			f.write(driver.page_source)
		with open('team.html') as f:
			team = f.read()



		#достаем все ссылки на матчи N-ой команды           ##-##
		s = BeautifulSoup(team , 'lxml').find_all(class_ = 'match-link match-report rc')

		match_data = []

		for item in s:

			match_data += [ item.get('href')]

		match_data = [('https://1xbet.whoscored.com/'+x).replace('MatchReport' , 'Live') for x in match_data if x != None]   ##-##
		print(match_data)
		sleep(5)

	except Exception as ex:
		print(ex)

	finally:
		driver.close()
		driver.quit()

	return match_data


data_item = {}
data_item_1 = {}
headers = {}

def get_ancidents(link):
	global data_item
	global data_item_1
	global headers
	try:
		driver = webdriver.Chrome(
				executable_path = 'C:/Users/Денис/Desktop/Web/parser1/chromedriver.exe'		
			)

		driver.get(link)
		with open('match_html.html' , 'w' , encoding = 'utf-8') as f:
			f.write(driver.page_source)

		with open('match_html.html') as f:
			r = f.read()

		sleep(4) 

		soup = BeautifulSoup(r , 'lxml').find(class_ = 'grid').find_all('tr')
		data = {}
		home_ancidents , away_ancidents = [] , []

		headers = {'teams ' : '' , 'result ' : ''}

		statistic = BeautifulSoup(r , 'lxml')

		headers['teams '] = str(statistic.find_all(class_ = 'team-link')[0].text) + ' - ' + str(statistic.find_all(class_ = 'team-link')[1].text)
		result = statistic.find(class_ = 'result').text
		stat = statistic.find_all('dl')
		numeric = []
		head = []
		headers['result '] = result
		for item in stat:

			for s in item.find_all('dd'):
				numeric += [s.text]
			for q in item.find_all('dt'):
				head += [q.text]

		for item , object in zip(numeric[:-1] , head[:-1]):
			headers[object] = item



		for home in soup:
			
			if home.find(class_ = 'key-incident home-incident'):
				home = home.find(class_ = 'key-incident home-incident')
				home_ancidents += [home]

		for away in soup:

			if away.find(class_ = 'key-incident away-incident'):
				away = away.find(class_ = 'key-incident away-incident')
				away_ancidents += [away]

			
		q_time = ''
		object_add = []
		object = ''
		object_add_card = ''
		key = False

		# скретчинг колонки -- HOME
		for x,area in enumerate([home_ancidents , away_ancidents]):
			for item in area:
				try:
					if any(x in str(item.find(class_='player-name').find_previous().get('title')) for x in ['yellow' , 'red']):
						object_add_card = item.find(class_='player-name').find_previous().get('title')
						key = True
					
					try:
						if object_add_card == '':
							if any(x in str(item.find(class_='incident-icon').find_previous().get('title')) for x in ['yellow' , 'red']):
								object_add_card = item.find(class_='incident-icon').find_previous().get('title')
								key = True
					except: pass


				except Exception as ex:
					pass

				try:
					if item.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'):
						object = str(item.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'))
						name = item.find(class_ = 'player-name').text

						try:
							object_add_name = item.find(class_= 'match-centre-header-team-key-incident has-related-event').find(class_ = 'player-name').text
						except:
							pass
						
						#остальные колонки с 2+ событиями
						try:
							if len(item.find_all(class_ = 'match-centre-header-team-key-incident has-related-event')) > 1:
								for q in item:
									try:
										object_add_name = item.find(class_ = 'match-centre-header-team-key-incident has-related-event').find_next_sibling('div').find(class_ = 'player-name').text
										object_add += [q.get('title')]
									except: pass
						except: pass
									


						
						if 'GOAL!' in object and 'Assisted' in object:
							object = f'GOAL by {object_add_name} assisted by {name}'
						
						if 'GOAL!' in object and 'Assisted' not in object:
							object = f'GOAL by {name}'

						
						object_add = [x for x in object_add if x != None]
						q_time = int(item.find(class_ = 'incident-icon').get('data-minute'))+1
						
						if x == 0:
							if object in object_add:
								data_item[ ' '.join(object_add)] = q_time
							else:
								data_item[ object , ' '.join(object_add)] = q_time

						elif x == 1:
							if object in object_add:
								data_item_1[ ' '.join(object_add)] = q_time
							else:
								data_item_1[ object , ' '.join(object_add)] = q_time

						
						object_add = []
						object_add_card = ''




				except:

					if key:
						q_time = int(item.find(class_ = 'incident-icon').get('data-minute'))+1
						if x == 0:
							data_item[object_add_card] = q_time
						else:
							data_item_1[object_add_card] = q_time
						key = False

					object = ''
					q_time = ''
					object_add_name = ''
					object_add = []
					object_add_card = ''
					try:
						theonlyone = item.find(class_='match-centre-header-team-key-incident').get('title')
						theonlyone_name = item.find(class_='match-centre-header-team-key-incident').find(class_ = 'player-name').text

						if 'GOAL!' in theonlyone and 'Assisted' not in theonlyone:
							object = f'GOAL by {theonlyone_name}'

						q_time = int(item.find(class_ = 'incident-icon').get('data-minute'))+1
						if x == 0:
							data_item[object , object_add] = q_time
						else:
							data_item_1[object , object_add] = q_time


					except:
						pass
		element = driver.find_element_by_class_name('noUi-touch-area')
		value = driver.find_elements_by_class_name('noUi-tooltip')
		value = int(eval(value[1].get_attribute('textContent')))

		iteri = 10.309

		data = {

		'Ratings' : '',
		'Total Shots' : '',
		'Possession%' : '',
		'Pass Success%' : '',
		'Dribbles' : '',
		'Aerials Won' : '' ,
		'Tackles' : '',
		'Corners' : '',
		'Dispossessed' : '' , 

		}
		print(list(x for x in data.keys()))
		q = 0

		for i in range(value+10):
			print(i+1)
			move = ActionChains(driver)

			statistic = driver.page_source
			statistic = BeautifulSoup(statistic , 'lxml').find(class_ = 'match-centre-stats')

			for item in statistic:
				item = item.find_all(class_ = re.compile('match-centre-stat selected|match-centre-stat has-stats'))

				for object in item:

					values = object.find_all(class_ = re.compile('match-centre-stat-value|match-centre-stat-value greater'))
					data[object.find(class_= 'match-centre-stat-values').previous_element] += str(values[0].text) + ','


			move.click_and_hold(element).move_by_offset(10.309 , 0).release().perform()

		inf = list(data.values())


		Ratings = inf[0].split(',')[::-1]
		Total_Shots = inf[1].split(',')[::-1]
		Possession = inf[2].split(',')[::-1]
		Pass_Success = inf[3].split(',')[::-1]
		Dribbles = inf[4].split(',')[::-1]
		Aerials_Won = inf[5].split(',')[::-1]
		Tackles = inf[6].split(',')[::-1]
		Corners = inf[7].split(',')[::-1]
		Dispossessed = inf[8].split(',')[::-1]

		#['Ratings','Total Shots','Possession%','Pass Success%','Dribbles','Aerials Won','Tackles','Corners','Dispossessed']

		q = headers['teams ']
		with open(f'{q} -data.csv' , 'w' , newline = '') as f:
			writer = csv.writer(f , delimiter = ';')
			writer.writerow(['','Ratings','Total Shots','Possession%','Pass Success%','Dribbles','Aerials Won','Tackles','Corners','Dispossessed'])
			for i in range(1,value+4):
				if i == 1:
					print(Ratings[i-1])

				writer.writerow([i , str(Ratings[i-1]).replace('- ' , '--'),str(Total_Shots[i-1]).replace('- ' , '--'),str(Possession[i-1]).replace('- ' , '--'),str(Pass_Success[i-1]).replace('- ' , '--'),str(Dribbles[i-1]).replace('- ' , '--'),str(Aerials_Won[i-1]).replace('- ' , '--'),str(Tackles[i-1]).replace('- ' , '--'),str(Corners[i-1]).replace('- ' , '--'),str(Dispossessed[i-1]).replace('- ' , '--')])

		return [data_item_1 , data_item]
	except Exception as ex:
		print(ex)

	finally:
		driver.close()
		driver.quit()



def data_ancidents(x):
	global data_item
	global data_item_1
	global headers
	data = {}
	datacheck1 = set()

	for i in data_item.values():
		for o in data_item_1.values():
			datacheck1.add(i)
			datacheck1.add(o)

	datacheck1 = sorted(datacheck1)
	
	for x in range(len(data_item.keys())+20):
		try:
			data[datacheck1[x]] = str(list(data_item.keys())[list(data_item.values()).index(datacheck1[x])]) + ' : '
		except:
			pass


	for x in range(len(data_item_1.keys())+20):
		try:
			try:
				data[datacheck1[x]] += '   :   '+ str(list(data_item_1.keys())[list(data_item_1.values()).index(datacheck1[x])])
			except:
				data[datacheck1[x]] = str(list(data_item_1.keys())[list(data_item_1.values()).index(datacheck1[x])])
		except:
			pass
	q = headers['teams ']

	with open(f'{q}.json', 'w') as f:
		json.dump(headers, f  , indent = 4 , ensure_ascii = False)
	with open(f'{q}.json', 'a') as f:
		json.dump(data, f  , indent = 4 , ensure_ascii = False)

	datacheck1 = set()
	data_item = {}
	data_item_1 = {}
	headers = {}

#def get_match_stat(link):

	try:
		driver = webdriver.Chrome(
				executable_path = 'C:/Users/Денис/Desktop/Web/parser1/chromedriver.exe'		
			)

		driver.get(link)
		with open('match_html.html' , 'w' , encoding = 'utf-8') as f:
			f.write(driver.page_source)

		with open('match_html.html') as f:
			r = f.read()

		sleep(4) 

		soup = BeautifulSoup(r , 'lxml').find(class_ = 'grid').find_all('tr')
		data = {}

		home_ancidents , away_ancidents = [] , []

		for home in soup:
			
			if home.find(class_ = 'key-incident home-incident'):
				home = home.find(class_ = 'key-incident home-incident')
				home_ancidents += [home]

		for away in soup:

			if away.find(class_ = 'key-incident away-incident'):
				away = away.find(class_ = 'key-incident away-incident')
				away_ancidents += [away]

		data_item = {}		
		q_time = ''
		object_add = []
		object = ''

		# скретчинг колонки -- HOME
		for item_home in home_ancidents:
		
			try:
				if item_home.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'):
					object = str(item_home.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'))
					name = item_home.find(class_ = 'player-name').text

					try:
						object_add_name = item_home.find(class_= 'match-centre-header-team-key-incident has-related-event').find(class_ = 'player-name').text
					except:
						pass

					#остальные колонки с 2+ событиями
					if len(item_home.find_all(class_ = 'match-centre-header-team-key-incident has-related-event')) > 1:
						for q in item_home:
							try:
								object_add_name = item_home.find(class_ = 'match-centre-header-team-key-incident has-related-event').find_next_sibling('div').find(class_ = 'player-name').text
								object_add += [q.get('title')]
							except: pass


					if 'GOAL!' in object and 'Assisted' in object:
						object = f'GOAL by {object_add_name} assisted by {name}'
					
					if 'GOAL!' in object and 'Assisted' not in object:
						object = f'GOAL by {name}'



					q_time = int(item_home.find(class_ = 'incident-icon').get('data-minute'))+1
					data_item[object , object_add] = q_time


			except:
				object = ''
				q_time = ''
				object_add_name = ''
				object_add = []
				try:
					theonlyone = item_home.find(class_='match-centre-header-team-key-incident').get('title')
					theonlyone_name = item_home.find(class_='match-centre-header-team-key-incident').find(class_ = 'player-name').text

					if 'GOAL!' in theonlyone and 'Assisted' not in theonlyone:
						object = f'GOAL by {theonlyone_name}'

					q_time = int(item_home.find(class_ = 'incident-icon').get('data-minute'))+1
					data_item[(object , ' '.join(object_add))] = q_time

				except:
					pass

		data_item_1 = {}		
		q_time = ''
		object_add = []
		object = ''


		for item_away in away_ancidents:
			try:
				if item_away.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'):
					object = str(item_away.find(class_ = 'match-centre-header-team-key-incident has-related-event').get('title'))
					name = item_away.find(class_ = 'player-name').text


					try:
						object_add_name = item_away.find(class_= 'match-centre-header-team-key-incident has-related-event').find(class_ = 'player-name').text
					except:
						pass

					#остальные колонки с 2+ событиями
					if len(item_away.find_all(class_ = 'match-centre-header-team-key-incident has-related-event')) > 1:
						for q in item_away:
							try:
								object_add_name = item_away.find(class_ = 'match-centre-header-team-key-incident has-related-event').find_next_sibling('div').find(class_ = 'player-name').text
								object_add += [q.get('title')]
							except: pass



					if 'GOAL!' in object and 'Assisted' in object:
						object = f'GOAL by {object_add_name} assisted by {name}'
					
					if 'GOAL!' in object and 'Assisted' not in object:
						object = f'GOAL by {name}'

					object_add = [x for x in object_add if x != None]

					q_time = int(item_away.find(class_ = 'incident-icon').get('data-minute'))+1
					data_item_1[(object , ' '.join(object_add))] = q_time


			except Exception as ex:

				object = ''
				q_time = ''
				object_add_name = ''
				object_add = []
				try:
					theonlyone = item_away.find(class_='match-centre-header-team-key-incident').get('title')
					theonlyone_name = item_away.find(class_='match-centre-header-team-key-incident').find(class_ = 'player-name').text

					if 'GOAL!' in theonlyone and 'Assisted' not in theonlyone:
						object = f'GOAL by {theonlyone_name}'

					q_time = int(item_away.find(class_ = 'incident-icon').get('data-minute'))+1
					data_item_1[object , object_add] = q_time

				except:
					pass	
		data = {}
		datacheck = []
		datacheck1 = set()


		for i in data_item.values():
			for o in data_item_1.values():
				datacheck1.add(i)
				datacheck1.add(o)

		datacheck1 = sorted(datacheck1)

		for x in range(len(data_item.keys())+2):
			try:
				data[datacheck1[x]] = str(list(data_item.keys())[list(data_item.values()).index(datacheck1[x])]) + ' : '
			except:
				pass


		for x in range(len(data_item_1.keys())+10):
			try:
				data[datacheck1[x]] = ' : '+ str(list(data_item_1.keys())[list(data_item_1.values()).index(datacheck1[x])])
			except:
				pass
		data = dict(sorted(data.items() , key = lambda item: item[0]))

		with open('f_ancidents.json', 'w') as f:
			json.dump(data , f  , indent = 4 , ensure_ascii = False)

	except Exception as ex:
		print(ex)

	finally:
		driver.close()
		driver.quit()#б
def get_html(url):

	try:

		driver = webdriver.Chrome(
			executable_path = 'C:/Users/Денис/Desktop/Web/parser1/chromedriver.exe'
		)

		driver.get(url)
		sleep(5)

		element = driver.find_element_by_class_name('noUi-touch-area')
		value = driver.find_elements_by_class_name('noUi-tooltip')
		value = int(eval(value[1].get_attribute('textContent')))

		iteri = 10.309

		data = {

		'Ratings' : '',
		'Total Shots' : '',
		'Possession%' : '',
		'Pass Success%' : '',
		'Dribbles' : '',
		'Aerials Won' : '' ,
		'Tackles' : '',
		'Corners' : '',
		'Dispossessed' : '' , 

		}
		print(list(x for x in data.keys()))
		q = 0

		for i in range(value+10):
			print(i+1)
			move = ActionChains(driver)

			statistic = driver.page_source
			statistic = BeautifulSoup(statistic , 'lxml').find(class_ = 'match-centre-stats')

			for item in statistic:
				item = item.find_all(class_ = re.compile('match-centre-stat selected|match-centre-stat has-stats'))

				for object in item:

					values = object.find_all(class_ = re.compile('match-centre-stat-value|match-centre-stat-value greater'))
					data[object.find(class_= 'match-centre-stat-values').previous_element] += str(values[0].text) + ','




			move.click_and_hold(element).move_by_offset(10.309 , 0).release().perform()

		inf = list(data.values())


		Ratings = inf[0].split(',')
		Total_Shots = inf[1].split(',')
		Possession = inf[2].split(',')
		Pass_Success = inf[3].split(',')
		Dribbles = inf[4].split(',')
		Aerials_Won = inf[5].split(',')
		Tackles = inf[6].split(',')
		Corners = inf[7].split(',')
		Dispossessed = inf[8].split(',')

		#['Ratings','Total Shots','Possession%','Pass Success%','Dribbles','Aerials Won','Tackles','Corners','Dispossessed']

		with open('data.csv' , 'w' , newline = '') as f:
			writer = csv.writer(f , delimiter = ';')
			writer.writerow(['','Ratings','Total Shots','Possession%','Pass Success%','Dribbles','Aerials Won','Tackles','Corners','Dispossessed'])
			for i in range(2,96):

				writer.writerow([i , str(Ratings[i-1]).replace('- ' , '--'),str(Total_Shots[i-1]).replace('- ' , '--'),str(Possession[i-1]).replace('- ' , '--'),str(Pass_Success[i-1]).replace('- ' , '--'),str(Dribbles[i-1]).replace('- ' , '--'),str(Aerials_Won[i-1]).replace('- ' , '--'),str(Tackles[i-1]).replace('- ' , '--'),str(Corners[i-1]).replace('- ' , '--'),str(Dispossessed[i-1]).replace('- ' , '--')])

	except Exception as ex:
		print(ex)
	finally:
		driver.close()
		driver.quit()



q = get_links('https://1xbet.whoscored.com/Teams/26/Show' , 'Liverpool')

for qs,item in enumerate(q):
	get_ancidents(item)
	data_ancidents(qs)
 '''
            for item in info:
                item = re.sub('{| |\n|"|}', '' , item)
                new_info += [item]

        


        for iteri in range(100000):
            try:
                sodata[new_info[count]] = new_info[count+1]
                count += 2
            except Exception as ex:
                pass
        flag1 = False
        for item , object in zip(sodata.keys() , sodata.values()):
            print(str(item) + ' | ' + str(object))
            flag1 = True

        if flag1:
            return 1
        qqqqq               '''