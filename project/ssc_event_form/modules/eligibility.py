def check(form):
    return (
        int(form['attendance']) < 200 and
        form['alcohol'] == "No" and
        form['duration'] != "More"
    )