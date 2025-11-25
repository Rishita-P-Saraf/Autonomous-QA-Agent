# demo_scripts/example_selenium.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_checkout():
    # Update this path to your local checkout.html
    driver = webdriver.Chrome()
    driver.get("C:\Users\rishi\GFG ML and DS course\OceanAI asmt 2\backend\assets\checkout.html")

    # --- Add Items ---
    driver.find_element(By.ID, "add_item1").click()
    driver.find_element(By.ID, "qty_item1").clear()
    driver.find_element(By.ID, "qty_item1").send_keys("2")

    driver.find_element(By.ID, "add_item2").click()
    driver.find_element(By.ID, "qty_item2").clear()
    driver.find_element(By.ID, "qty_item2").send_keys("1")

    # --- Apply Discount Code ---
    discount_input = driver.find_element(By.ID, "discount_code")
    discount_input.clear()
    discount_input.send_keys("SAVE15")

    # --- Fill User Details ---
    driver.find_element(By.ID, "name").send_keys("John Doe")
    driver.find_element(By.ID, "email").send_keys("john@example.com")
    driver.find_element(By.ID, "address").send_keys("123 Main St")

    # --- Select Shipping ---
    driver.find_element(By.CSS_SELECTOR, 'input[name="shipping"][value="Express"]').click()

    # --- Select Payment ---
    driver.find_element(By.CSS_SELECTOR, 'input[name="payment"][value="Credit Card"]').click()

    # --- Click Pay Now ---
    driver.find_element(By.ID, "pay_now").click()

    # Wait for success message
    time.sleep(1)
    success_msg = driver.find_element(By.ID, "payment_msg").text
    print("Payment Message:", success_msg)

    assert success_msg == "Payment Successful!", "Payment did not succeed!"

    time.sleep(2)
    driver.quit()


if __name__ == "__main__":
    test_checkout()
