from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

class CourseCompassPage:
    """Page-Object Model for Selenium E2E testing (Phase 4.5)."""
    def __init__(self, driver):
        self.driver = driver

    def open(self, url="http://localhost:3000"):
        self.driver.get(url)
        time.sleep(1)

    def select_student(self, student_id):
        dropdown = Select(self.driver.find_element(By.ID, "student-select"))
        dropdown.select_by_value(student_id)
        time.sleep(1)

def run_e2e():
    driver = webdriver.Chrome()
    try:
        page = CourseCompassPage(driver)
        page.open()
        page.select_student("STU-103")
        assert "PREREQUISITE LOCKED" in driver.page_source
        page.select_student("STU-101")
        assert "Enrol Now" in driver.page_source
        print("Selenium E2E Test Passed!")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_e2e()
