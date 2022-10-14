import importlib
importlib.reload(exmo)
from exmo import *
s = exchange(s.driver)

#man = api_class(original,'fuckyou')

s.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find_all('div',{'class': re.compile('TransferButton')})[0])))).click()
freeze(s.driver)