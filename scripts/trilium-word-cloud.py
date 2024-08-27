#!/usr/bin/env python3

import sqlite3
from bs4 import BeautifulSoup
from collections import Counter
import re

exclude_words = set(
    [
        "to",
        "the",
        "and",
        "of",
        "at",
        "a",
        "my",
        "in",
        "com",
        "that",
        "it",
        "but",
        "is",
        "was",
        "i",
        "do",
        "be",
        "get",
        "for",
        "on",
        "with",
        "as",
        "you",
        "this",
        "me",
        "you",
    ]
)

with open("/usr/share/dict/words", "r") as myfile:
    data = myfile.readlines()
    allwords = set([x.strip().lower() for x in data])
# Connect to your SQLite database
conn = sqlite3.connect("/home/kevin/.local/share/trilium-data/document.db")
cursor = conn.cursor()

# Execute the SQL query
cursor.execute("""
    SELECT blobs.content
    FROM notes
    JOIN blobs ON notes.blobId = blobs.blobId
    WHERE notes.isDeleted = 0 AND notes.type = 'text'
    -- AND notes.title NOT LIKE "note-20%";
""")
rows = cursor.fetchall()

# Initialize a counter for word frequencies
word_counter = Counter()

# Process each content
for row in rows:
    content = row[0]

    # Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()

    # Tokenize the text and count words
    words = re.findall(r"\w+", text.lower())  # Convert to lowercase and find words
    words = [
        word
        for word in words
        if word in allwords and len(word) >= 2 and word not in exclude_words
    ]  # Filter out non interesting words
    word_counter.update(words)

# Output the most common words
most_common_words = word_counter.most_common(200)  # Get the top 100 most common words
print(most_common_words)

# Close the connection
conn.close()

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Convert the counter to a dictionary for the word cloud
word_freq = dict(most_common_words)

# Generate the word cloud
wordcloud = WordCloud(
    width=1600, height=800, background_color="white"
).generate_from_frequencies(word_freq)

# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
