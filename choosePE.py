import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


# 创建 WebDriver 对象
# wd = webdriver.Chrome()


def click_with_retry(wd, xpath, max_attempts=3):
    """尝试点击元素，如果失败则重试"""
    attempt = 0
    while attempt < max_attempts:
        try:
            # 显式等待元素可点击
            element = WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            # 滚动到元素
            wd.execute_script("arguments[0].scrollIntoView(true);", element)
            # 点击元素
            element.click()
            # print(f"成功点击元素: {xpath}")
            return True
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException) as e:
            attempt += 1
            # print(f"点击元素失败，尝试第 {attempt} 次: {e}")
            time.sleep(2)  # 等待 2 秒再重试
    return False

def click_center_of_element(wd, element):
    try:
        # 使用 ActionChains 移动到元素的正中央并点击
        actions = ActionChains(wd)
        actions.move_to_element(element).click().perform()
        print("点击方框正中央成功")
        return True
    except Exception as e:
        print(f"点击方框正中央时发生错误: {e}")
    return False

def select_course(wd):
    try:
        time.sleep(3)
        # 滚动页面直到“体育课程”按钮可见并点击
        if not click_with_retry(wd, "//a[@id='aSportCourse']"):
            print("无法点击体育课程按钮，重新启动程序")
            wd.quit()  # 关闭当前的 WebDriver 实例
            main()  # 重新启动程序
            return True

        time.sleep(2)

        # 查找并点击 "陆上赛艇" 课程
        rowing_course_xpath = "//div[contains(text(),'陆上赛艇')]"
        if not click_with_retry(wd, rowing_course_xpath):
            print("无法点击陆上赛艇课程")
            return False

        time.sleep(2)

        # 查找课程，遍历检查是否有可选状态
        course_divs = wd.find_elements(By.XPATH,
                                       "//span[contains(@class, 'cv-info-title')]")
        # course_divs = wd.find_elements(By.XPATH,
        #                                "//span[contains(@class, 'cv-info-title') and contains(text(),'孙蔚')]")

        for course_div in course_divs:
            course_container = course_div.find_element(By.XPATH, "./../../..")
            try:
                # 检查是否有"可选"状态
                capacity_status = course_container.find_element(By.XPATH, ".//div[contains(@class, 'cv-caption-text')]")
                # print(f"课程状态: {capacity_status.text}")
                if "不可选" not in capacity_status.text and "可选" in capacity_status.text:
                    print("该课程可选，准备选课...")

                    # 获取课程的id（即tcid）
                    course_id = course_container.get_attribute('id')
                    tcid_value = course_id.replace('_courseDiv', '')  # 从id中提取tcid
                    print(f"id:{tcid_value}")

                    if click_center_of_element(wd, course_container):
                        # 确认选择
                        confirm_button_xpath = f"//button[@class='cv-btn cv-btn-chose' and @tcid='{tcid_value}']"
                        if click_with_retry(wd, confirm_button_xpath):
                            print("课程已成功选择")
                            return True
                else:
                    print(f"课程不可选，状态为: {capacity_status.text}")

            except NoSuchElementException:
                print("未找到课程状态，跳过此课程")

        print("所有课程均不可选，继续刷新...")
        return False

    except NoSuchElementException as e:
        print(f"出现错误：{e}")
        return False


def main():
    # 打开选课系统
    wd = webdriver.Chrome()
    wd.implicitly_wait(6)
    wd.get('http://xkfw.xjtu.edu.cn/')
    time.sleep(2)
    wd.maximize_window()
    time.sleep(2)

    # 输入用户名
    username_field = wd.find_element(By.NAME, "username")
    username_field.send_keys("你的学号")

    # 输入密码
    password_field = wd.find_element(By.NAME, "pwd")
    password_field.send_keys("你的密码")

    # 点击登录按钮
    login_button = wd.find_element(By.ID, "account_login")
    login_button.click()

    # 等待页面加载并找到确认按钮
    try:
        """
        confirm_button = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.bh-btn.bh-btn-primary.bh-pull-right"))
        )
        confirm_button.click()
        """

        # 开始选课
        start_course_button = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.ID, "courseBtn"))
        )
        start_course_button.click()
        print("开始选课按钮已点击")

        # 循环检查并选课，直到成功
        while True:
            success = select_course(wd)
            if success:
                break
            time.sleep(3)
            wd.refresh()

    except TimeoutException as e:
        print(f"发生错误: {e}")
    finally:
        wd.quit()


if __name__ == "__main__":
    main()

