from datetime import date

current_year = date.today().year
copyright_holder = "Your GitHub Username"

# Read the template file
with open("LICENSE_template.txt", "r") as f:
    template = f.read()

# Replace placeholders with actual values
license_text = template.format(currentYear=current_year, copyrightHolder=copyright_holder)

# Write the license text to the new file
with open("LICENSE", "w") as f:
    f.write(license_text)
