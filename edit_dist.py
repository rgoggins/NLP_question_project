def calculateLevenshteinDistance(str1, str2):
  """
  TODO:
    take two strings and calculate their Levenshtein Distance for task 1
    return an integer which is the distance
  """
  m = len(str1)
  n = len(str2)
  table = [[0 for col in range(n+1)] for row in range(m+1)]
  for row in range(m+1):
    for col in range(n+1):
      if row== 0: #set initial values
        table[row][col] = col

      if col == 0: #set initial values
        table[row][col] = row

      elif str1[row-1] != str2[col-1]:
        table[row][col] = min(table[row][col-1] + 1, table[row-1][col] + 1, table[row-1][col-1] + 1)

      else:
        table[row][col] = table[row-1][col-1]

  return table[m][n]
