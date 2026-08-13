import secrets
import string
import math
import re
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# ADVANCED PASSWORD GENERATOR & STRENGTH CHECKER
# WITH INTEGRATED DATA ANALYTICS DASHBOARD
# ============================================

COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty",
    "abc123", "password123", "admin", "welcome",
    "letmein", "iloveyou", "000000", "111111",
    "123123", "monkey", "dragon", "football"
}


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class PasswordManager:

    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.numbers = string.digits
        self.symbols = "!@#$%^&*()-_=+[]{}<>?/"
        self.records = []   # stores every generated password's analytics data

    # --------------------------------------
    # Generate Secure Password
    # --------------------------------------
    def generate_password(self, length, use_lower=True, use_upper=True,
                           use_numbers=True, use_symbols=True):

        character_pool = ""
        password = []

        if use_lower:
            character_pool += self.lowercase
            password.append(secrets.choice(self.lowercase))

        if use_upper:
            character_pool += self.uppercase
            password.append(secrets.choice(self.uppercase))

        if use_numbers:
            character_pool += self.numbers
            password.append(secrets.choice(self.numbers))

        if use_symbols:
            character_pool += self.symbols
            password.append(secrets.choice(self.symbols))

        if not character_pool:
            raise ValueError("At least one character type must be selected.")

        while len(password) < length:
            password.append(secrets.choice(character_pool))

        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    # --------------------------------------
    # Calculate Entropy
    # --------------------------------------
    def calculate_entropy(self, password):
        charset = 0
        if re.search(r"[a-z]", password):
            charset += 26
        if re.search(r"[A-Z]", password):
            charset += 26
        if re.search(r"[0-9]", password):
            charset += 10
        if re.search(r"[!@#$%^&*()\-_=+\[\]{}<>?/]", password):
            charset += 22

        entropy = len(password) * math.log2(charset) if charset else 0
        return round(entropy, 2)

    # --------------------------------------
    # Estimate Crack Time (offline, 10 billion guesses/sec)
    # --------------------------------------
    def estimate_crack_time(self, entropy):
        guesses = 2 ** entropy
        seconds = guesses / (10 ** 10)

        units = [
            ("years", 60 * 60 * 24 * 365),
            ("days", 60 * 60 * 24),
            ("hours", 60 * 60),
            ("minutes", 60),
            ("seconds", 1),
        ]

        for name, unit_seconds in units:
            if seconds >= unit_seconds:
                value = seconds / unit_seconds
                return f"{value:,.2f} {name}"

        return "Instantly"

    # --------------------------------------
    # Password Strength Checker
    # --------------------------------------
    def check_strength(self, password):
        score = 0
        remarks = []

        if len(password) >= 8:
            score += 1
        else:
            remarks.append("Increase password length to at least 8 characters.")

        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            remarks.append("Include uppercase letters.")

        if re.search(r"[a-z]", password):
            score += 1
        else:
            remarks.append("Include lowercase letters.")

        if re.search(r"\d", password):
            score += 1
        else:
            remarks.append("Include numbers.")

        if re.search(r"[!@#$%^&*()\-_=+\[\]{}<>?/]", password):
            score += 1
        else:
            remarks.append("Include special characters.")

        if password.lower() in COMMON_PASSWORDS:
            remarks.append("This is a commonly used password.")
            score = 0

        entropy = self.calculate_entropy(password)
        crack_time = self.estimate_crack_time(entropy)

        if score <= 2:
            strength, color = "Very Weak", Colors.RED
        elif score <= 4:
            strength, color = "Weak", Colors.RED
        elif score <= 5:
            strength, color = "Medium", Colors.YELLOW
        elif score == 6:
            strength, color = "Strong", Colors.GREEN
        else:
            strength, color = "Very Strong", Colors.CYAN

        return {
            "strength": strength,
            "score": score,
            "entropy": entropy,
            "crack_time": crack_time,
            "remarks": remarks,
            "color": color
        }

    # --------------------------------------
    # Log a record for analytics
    # --------------------------------------
    def log_record(self, password, length, result, flags):
        self.records.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "score": result["score"],
            "strength": result["strength"],
            "entropy": result["entropy"],
            "crack_time": result["crack_time"],
            "lowercase": flags["lower"],
            "uppercase": flags["upper"],
            "numbers": flags["numbers"],
            "symbols": flags["symbols"],
        })

    # --------------------------------------
    # Export records to CSV
    # --------------------------------------
    def export_csv(self, filename="password_analytics.csv"):
        if not self.records:
            print(f"{Colors.YELLOW}No records to export.{Colors.RESET}")
            return
        df = pd.DataFrame(self.records)
        df.to_csv(filename, index=False)
        print(f"{Colors.GREEN}Exported {len(df)} records to {filename}{Colors.RESET}")

    # --------------------------------------
    # DATA ANALYTICS DASHBOARD
    # --------------------------------------
    def analytics_dashboard(self):
        if not self.records:
            print(f"{Colors.YELLOW}No data available yet. Generate some passwords first.{Colors.RESET}")
            return

        df = pd.DataFrame(self.records)

        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}{Colors.MAGENTA}        PASSWORD ANALYTICS SUMMARY{Colors.RESET}")
        print("=" * 60)
        print(f"Total Passwords Generated : {len(df)}")
        print(f"Average Length            : {df['length'].mean():.2f}")
        print(f"Average Entropy           : {df['entropy'].mean():.2f} bits")
        print(f"Average Score             : {df['score'].mean():.2f}/7")
        print("\nStrength Distribution:")
        print(df['strength'].value_counts().to_string())
        print("\nDescriptive Statistics (Entropy):")
        print(df['entropy'].describe().to_string())
        print("=" * 60)

        sns.set_style("darkgrid")
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Password Strength Analytics Dashboard", fontsize=16, fontweight="bold")

        # 1. Strength distribution bar chart
        strength_order = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
        counts = df['strength'].value_counts().reindex(strength_order).fillna(0)
        sns.barplot(x=counts.index, y=counts.values, palette="viridis", ax=axes[0, 0])
        axes[0, 0].set_title("Strength Category Distribution")
        axes[0, 0].set_xlabel("Strength")
        axes[0, 0].set_ylabel("Count")
        axes[0, 0].tick_params(axis='x', rotation=30)

        # 2. Entropy histogram
        sns.histplot(df['entropy'], bins=10, kde=True, color="teal", ax=axes[0, 1])
        axes[0, 1].set_title("Entropy Distribution")
        axes[0, 1].set_xlabel("Entropy (bits)")

        # 3. Length vs Entropy scatter
        sns.scatterplot(data=df, x="length", y="entropy", hue="strength",
                         palette="Set2", ax=axes[1, 0])
        axes[1, 0].set_title("Password Length vs Entropy")

        # 4. Character type usage
        usage = {
            "Lowercase": df['lowercase'].sum(),
            "Uppercase": df['uppercase'].sum(),
            "Numbers": df['numbers'].sum(),
            "Symbols": df['symbols'].sum(),
        }
        sns.barplot(x=list(usage.keys()), y=list(usage.values()), palette="mako", ax=axes[1, 1])
        axes[1, 1].set_title("Character Type Usage Count")

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        filename = "password_analytics_dashboard.png"
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"{Colors.GREEN}Dashboard saved as '{filename}'{Colors.RESET}")


# ============================================
# Main Program (Menu-Driven)
# ============================================

def get_yes_no(prompt):
    return input(prompt).strip().lower() == "y"


def generate_flow(manager):
    try:
        length = int(input("Password Length (Minimum 8): "))
        if length < 8:
            print(f"{Colors.RED}Password must be at least 8 characters.{Colors.RESET}")
            return

        count = int(input("How many passwords do you want to generate? : "))

        flags = {
            "lower": get_yes_no("Include Lowercase? (Y/N): "),
            "upper": get_yes_no("Include Uppercase? (Y/N): "),
            "numbers": get_yes_no("Include Numbers? (Y/N): "),
            "symbols": get_yes_no("Include Symbols? (Y/N): "),
        }

        print("\n" + "=" * 60)

        for i in range(count):
            password = manager.generate_password(
                length, flags["lower"], flags["upper"], flags["numbers"], flags["symbols"]
            )
            result = manager.check_strength(password)
            manager.log_record(password, length, result, flags)

            print(f"\nPassword {i+1}")
            print("-" * 50)
            print("Generated Password :", password)
            print(f"Strength           : {result['color']}{result['strength']}{Colors.RESET}")
            print(f"Security Score     : {result['score']}/7")
            print(f"Entropy            : {result['entropy']} bits")
            print(f"Est. Crack Time    : {result['crack_time']}")

            if result["remarks"]:
                print("\nSuggestions")
                for remark in result["remarks"]:
                    print(" •", remark)
            else:
                print(f"{Colors.GREEN}Excellent password. No improvements needed.{Colors.RESET}")

            print("-" * 50)

    except ValueError:
        print(f"{Colors.RED}Please enter valid numeric input.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")


def check_existing_flow(manager):
    pwd = input("Enter password to check: ")
    result = manager.check_strength(pwd)
    manager.log_record(pwd, len(pwd), result,
                        {"lower": bool(re.search(r"[a-z]", pwd)),
                         "upper": bool(re.search(r"[A-Z]", pwd)),
                         "numbers": bool(re.search(r"\d", pwd)),
                         "symbols": bool(re.search(r"[!@#$%^&*()\-_=+\[\]{}<>?/]", pwd))})

    print("-" * 50)
    print(f"Strength           : {result['color']}{result['strength']}{Colors.RESET}")
    print(f"Security Score     : {result['score']}/7")
    print(f"Entropy            : {result['entropy']} bits")
    print(f"Est. Crack Time    : {result['crack_time']}")
    if result["remarks"]:
        print("\nSuggestions")
        for remark in result["remarks"]:
            print(" •", remark)
    print("-" * 50)


def main_menu():
    manager = PasswordManager()

    while True:
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}{Colors.CYAN}   ADVANCED PASSWORD GENERATOR & ANALYTICS SUITE{Colors.RESET}")
        print("=" * 60)
        print("1. Generate New Password(s)")
        print("2. Check Strength of Existing Password")
        print("3. View Analytics Dashboard (Charts + Stats)")
        print("4. Export Session Data to CSV")
        print("5. Exit")
        print("=" * 60)

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            generate_flow(manager)
        elif choice == "2":
            check_existing_flow(manager)
        elif choice == "3":
            manager.analytics_dashboard()
        elif choice == "4":
            manager.export_csv()
        elif choice == "5":
            print(f"{Colors.GREEN}Thank you for using the Advanced Password Generator & Analytics Suite.{Colors.RESET}")
            break
        else:
            print(f"{Colors.RED}Invalid option. Please choose 1-5.{Colors.RESET}")


if __name__ == "__main__":
    main_menu()
