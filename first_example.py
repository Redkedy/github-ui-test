import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

####################
## Configurations ##
####################

load_dotenv()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD")
repo_name = "my-new-repo22"

file_path = os.path.join(os.path.dirname(__file__), "test.html")

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    #############################
    ### GitHub Giriş İşlemi ###
    #############################
    print("\n--- Giriş İşlemi Testi Yapılıyor ---\n")
    driver.delete_all_cookies()
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        '''
    })

    driver.get("https://github.com")
    time.sleep(1)

    sign_in_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign in")))
    assert sign_in_button is not None, "Sign in butonu bulunamadı!"
    sign_in_button.click()
    time.sleep(2)
    assert "login" in driver.current_url, "Login sayfasına yönlendirme başarısız!"

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    username_input.send_keys(GITHUB_USERNAME)
    assert username_input.get_attribute("value") == GITHUB_USERNAME, "Kullanıcı adı alanı doldurulamadı!"
    password_input.send_keys(GITHUB_PASSWORD)

    login_button = driver.find_element(By.NAME, "commit")
    assert login_button.is_enabled(), "Giriş butonu devre dışı!"
    login_button.click()
    time.sleep(0.5)
    current_url = driver.current_url.strip()
    
    # Başarı & hata kontrolü
    if "https://github.com/session" in current_url:
        print("❌ HATA: GitHub oturumu hatası veya işlem başarısız.")
        assert False, "Repo oluşturulamadı. Oturum hatası sayfasına yönlendi."
    elif current_url == "https://github.com/":
        print(" ✅ BAŞARILI: GitHub ana sayfaya yönlendirildi.")
    else:
        print(f"⚠️ Beklenmedik bir URL yönlendirmesi: {current_url}")


    print(" Giriş başarılı")
    time.sleep(5)
    assert "github.com" in driver.current_url, "Giriş sonrası ana sayfaya yönlendirme başarısız!"

    #############################
    ## Yeni Repo Oluşturma ##
    #############################
    print("\n--- Repo Oluşturma Testi Yapılıyor ---\n")
    driver.get("https://github.com/new")
    time.sleep(2)

    repo_name_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-required="true"]')))
    repo_name_input.send_keys(repo_name)
    assert repo_name_input.get_attribute("value") == repo_name, "Repo adı yazılamadı!"
    time.sleep(0.5)
    repo_id_name = "RepoNameInput"
    repo_available = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[@class='prc-components-ValidationText-jjsBp']"
    )))

    repo_available_text=repo_available.text.lower()
    print(repo_available_text)
    assert "available " not in repo_available_text, "bu repo bulunmaktadır."
    
    repo_description = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Description"]')))
    
    repo_description.send_keys("This is my new repository created using Selenium.")
    assert "Selenium" in repo_description.get_attribute("value"), "Açıklama yazılamadı!"
    time.sleep(3)
    create_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[5]/main/react-app/div/form/div[6]/button'))) 
                                        
    create_button.click()
    time.sleep(3)
    assert repo_name in driver.current_url, "Repo oluşturulamadı!"

    ##################
    ## Upload Files ##
    ##################
    print("\n--- Upload Testi Yapılıyor ---\n")
    driver.get(f"https://github.com/{GITHUB_USERNAME}?tab=repositories")
    time.sleep(2)

    repo_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@itemprop='name codeRepository' and contains(text(), '{repo_name}')]")))
    repo_link.click()
    time.sleep(2)
    assert repo_name in driver.current_url, "Repo sayfasına gidilemedi!"
    

    upload_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'uploading an existing file')]")))
    upload_link.click()
    time.sleep(1)

    file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    assert file_input.is_displayed(), "Dosya yükleme alanı görünmüyor!"
    file_input.send_keys(file_path)
    time.sleep(2)

    commit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Commit changes')]")))
    commit_button.click()
    time.sleep(3)

    assert "test.html" in driver.page_source, "test.html dosyası yüklenmedi!"
    print("✅ Dosya başarıyla yüklendi.")

    ##################
    ## Search Files ##
    ##################
    print("\n--- Searching Testi Yapılıyor ---\n")
    searchText = "repo:ahmetkurt-dev/ahmetkurt-dev "
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/header/div/div[2]/div[1]/qbsearch-input/div[1]/div[1]/div/div/button"))
    )
    search_button.click()
    time.sleep(1)

    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "query-builder-test"))
    )
    search_box.clear()
    search_box.send_keys(searchText)
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)

    repo_item= driver.find_element(By.XPATH,'//*[@id="folder-row-1"]/td[2]/div/div/div/div/a')
   
    assert repo_item is not None, "Aranan repo bulunamadı!"
    repo_item.click()
    time.sleep(2)
    print("\n--- Dosya İndirme Testi Yapılıyor ---\n")
    #########################
    ## Dosya İndirme Butonu ##
    #########################

    download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="download-raw-button"]')))
    assert download_button.is_displayed(), "İndirme butonu görünmüyor!"
    download_button.click()
    print("✅ Dosya başarıyla indirildi.")
    time.sleep(2)

    #########################
    ## Log out ##
    #########################
    print("\n---Log out Yapılıyor ---\n")
    driver.get("https://github.com/logout")
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/main/div/div[3]/div/div[2]/form"))).click()
    time.sleep(3)

except Exception as e:
    import traceback
    print("❌ Test sırasında hata oluştu:")
    traceback.print_exc()


finally:
    driver.quit()
    print("🔚 Tarayıcı kapatıldı.")
