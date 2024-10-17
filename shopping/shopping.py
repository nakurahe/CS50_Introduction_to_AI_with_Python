import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )
    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename: str):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    month_dictionay = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4,
                       'June': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9,
                       'Nov': 10, 'Dec': 11}

    evidence = list()
    labels = list()
    with open(filename, mode='r') as file:
        csv_dict_file = csv.DictReader(file, delimiter=',')
        for row in csv_dict_file:
            temp = list()
            for key in row:
                if (key == 'Administrative'
                        or key == 'Informational'
                        or key == 'ProductRelated'
                        or key == 'OperatingSystems'
                        or key == 'Browser'
                        or key == 'Region'
                        or key == 'TrafficType'):
                    row[key] = int(row.get(key))
                elif (key == 'Administrative_Duration'
                        or key == 'Informational_Duration'
                        or key == 'ProductRelated_Duration'
                        or key == 'BounceRates'
                        or key == 'ExitRates'
                        or key == 'PageValues'
                        or key == 'SpecialDay'):
                    row[key] = float(row.get(key))
                elif key == 'Month':
                    row[key] = month_dictionay.get(row.get(key))
                elif key == 'VisitorType':
                    row[key] = 1 if row.get(key) == 'Returning_Visitor' else 0
                elif key == 'Weekend':
                    row[key] = 0 if row.get(key) == 'FALSE' else 1
                elif key == 'Revenue':
                    row[key] = 0 if row.get(key) == 'FALSE' else 1
                temp.append(row[key])
            evidence.append(temp[:-1])
            labels.append(temp[-1:])
    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels: list, predictions: list):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.

    >>> evaluate([1, 1, 0, 1, 0], [1, 0, 1, 1, 1])
    (0.5, 0.0)
    """
    num_of_positives_in_label = labels.count(1)
    num_of_negatives_in_label = labels.count(0)

    correct_positives = 0
    correct_negatives = 0
    for _ in range(len(labels)):
        if labels[_] == 1 and predictions[_] == 1:
            correct_positives += 1
        elif labels[_] == 0 and predictions[_] == 0:
            correct_negatives += 1

    return (correct_positives / num_of_positives_in_label,
            correct_negatives / num_of_negatives_in_label)


if __name__ == "__main__":
    main()
