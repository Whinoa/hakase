def str_get_first_number(str):
  # Gets first digit
  # See: https://stackoverflow.com/a/20008559
  return int(str[[char.isdigit() for char in str].index(True)])
