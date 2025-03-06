import os
import sys
import time
import requests
from colorama import Fore, Style, init
from datetime import datetime
import json
from tabulate import tabulate

init(autoreset=True)

class PocketFi:
    def __init__(self):
        self.line = Fore.WHITE + "~" * 50
        self.banner = f"""
        {Fore.BLUE}✨ Smart Airdrop {Fore.WHITE}PocketFi Auto Claimer ✨
        """
        
        self.api_url = {
            "mining_info": "https://gm.pocketfi.org/mining/getUser Mining",
            "claim_mining": "https://gm.pocketfi.org/mining/claimMining",
            "daily_boost": "https://bot2.pocketfi.org/boost/activateDailyBoost"
        }

    def clear_terminal(self):
        os.system("cls" if os.name == "nt" else "clear")

    def headers(self, data):
        return {
            "Accept": "application/json, text/plain, */*",
            "Telegramrawdata": f"{data}",
            "Origin": "https://pocketfi.app",
            "Referer": "https://pocketfi.app/",
            "User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

    def mining_info(self, data):
        headers = self.headers(data=data)
        response = requests.get(url=self.api_url["mining_info"], headers=headers)
        return response.json()

    def claim_mining(self, data):
        headers = self.headers(data=data)
        response = requests.post(url=self.api_url["claim_mining"], headers=headers)
        return response.json()

    def daily_boost(self, data):
        headers = self.headers(data=data)
        response = requests.post(url=self.api_url["daily_boost"], headers=headers)
        return response.json()

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {msg}")

    def display_status(self, account_data):
        table_data = [
            [
                Fore.CYAN + str(acc["no"]) + Style.RESET_ALL,
                Fore.GREEN + str(acc["balance"]) + Style.RESET_ALL,
                Fore.YELLOW + str(acc["mining_balance"]) + Style.RESET_ALL,
                Fore.MAGENTA + acc["status"] + Style.RESET_ALL
            ]
            for acc in account_data
        ]

        print("\n" + Fore.YELLOW + "=" * 80)
        print(Fore.GREEN + "✨ POCKETFI BOT STATUS ✨".center(80))
        print(Fore.YELLOW + "=" * 80 + Style.RESET_ALL)
        print(tabulate(
            table_data,
            headers=[
                Fore.CYAN + "Account No" + Style.RESET_ALL,
                Fore.GREEN + "Balance" + Style.RESET_ALL,
                Fore.YELLOW + "Mining Balance" + Style.RESET_ALL,
                Fore.MAGENTA + "Status" + Style.RESET_ALL
            ],
            tablefmt="fancy_grid"
        ))
        print("\n" + Fore.YELLOW + "=" * 80)

    def main(self):
        while True:
            self.clear_terminal()
            print(self.banner)
            try:
                with open("data.txt", "r") as file:
                    data_lines = file.read().splitlines()
            except FileNotFoundError:
                self.log(f"{Fore.RED}Error: data.txt file not found!")
                sys.exit(1)

            account_data = []
            num_acc = len(data_lines)
            self.log(self.line)
            self.log(f"{Fore.GREEN}Number of accounts: {Fore.WHITE}{num_acc}")

            for no, data in enumerate(data_lines):
                self.log(self.line)
                self.log(f"{Fore.GREEN}Account number: {Fore.WHITE}{no+1}/{num_acc}")

                account_info = {"no": no + 1, "data": data, "balance": 0, "mining_balance": 0, "status": ""}

                try:
                    mining_info = self.mining_info(data=data)
                    balance = mining_info["userMining"]["gotAmount"]
                    mining_balance = mining_info["userMining"]["miningAmount"]

                    account_info["balance"] = balance
                    account_info["mining_balance"] = mining_balance
                    account_info["status"] = "Fetched Mining Info"

                    self.log(f"{Fore.GREEN}Balance: {Fore.WHITE}{balance} - {Fore.GREEN}Mining Balance: {Fore.WHITE}{mining_balance}")
                    self.log(f"{Fore.YELLOW}Trying to claim...")

                    if mining_balance > 0:
                        claim_mining = self.claim_mining(data=data)
                        if claim_mining.get("userMining"):
                            account_info["balance"] = claim_mining["userMining"]["gotAmount"]
                            account_info["mining_balance"] = claim_mining["userMining"]["miningAmount"]
                            account_info["status"] = "Claimed Mining"
                            self.log(f"{Fore.WHITE}Claim Mining: {Fore.GREEN}Success")
                        else:
                            account_info["status"] = "Error Claiming Mining"
                            self.log(f"{Fore.WHITE}Claim Mining: {Fore.RED}Error")
                    else:
                        account_info["status"] = "No Mining Points to Claim"
                        self.log(f"{Fore.WHITE}Claim Mining: {Fore.RED}No points to claim")

                    self.log(f"{Fore.YELLOW}Trying to activate daily boost...")
                    activate_boost = self.daily_boost(data=data)
                    activate_status = activate_boost.get("updatedForDay")
                    if activate_status is not None:
                        account_info["status"] = "Activated Daily Boost"
                        self.log(f"{Fore.WHITE}Activate Daily Boost: {Fore.GREEN}Success")
                    else:
                        account_info["status"] = "Daily Boost Already Activated"
                        self.log(f"{Fore.WHITE}Activate Daily Boost: {Fore.RED}Already activated")

                except Exception as e:
                    account_info["status"] = f"Error: {e}"
                    self.log(f"{Fore.RED}Error: {e}")

                account_data.append(account_info)

            self.display_status(account_data)
            wait_time = 30 * 60  # Change to 30 minutes
            self.log(f"{Fore.YELLOW}Waiting for {int(wait_time/60)} minutes!")
            time.sleep(wait_time)

if __name__ == "__main__":
    try:
        pocketfi = PocketFi()
        pocketfi.main()
    except KeyboardInterrupt:
        sys.exit()