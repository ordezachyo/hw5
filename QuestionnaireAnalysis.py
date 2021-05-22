import pathlib

import numpy
import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
import math

class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname):
        self.data_fname = data_fname

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        with open(self.data_fname) as f:
            self.data = json.load(f)
            data_df = pd.DataFrame(self.data)
            self.data = data_df


    def show_age_distrib(self) : #-> Tuple[np.ndarray, np.ndarray]
        """Calculates and plots the age distribution of the participants.

            Returns
           -------
           hist : np.ndarray
            Number of people in a given bin
           bins : np.ndarray
          Bin edges
        """
        ages = self.data.age
        ages = ages.replace(['nan'], pd.NaT).copy()
        ages_clean = ages.dropna()
        fig, ax = plt.subplots()

        (n, bins,_) = plt.hist(ages_clean,[0,10,20,30,40,50,60,70,80,90,100])
        return n,bins

    def remove_rows_without_mail(self): #-> pd.DataFrame
        df = self.data.copy()


        for index, email in enumerate(self.data.email):
            result = True
            if email[0] == '@' or email [-1] == '@' or email.find('@') == -1:
                result = False
            elif email[email.find('@') +1] == '.':
                result = False
            if email[0] == '.' or email [-1] == '.' or email.find('.') == -1:
                result = False

            print(index, email, result)
            if result == False:
                df = df.drop(index).copy()
                #self.data = self.data.drop(index).copy()

        return df

    def fill_na_with_mean(self): #-> Tuple[pd.DataFrame, np.ndarray]:
        """Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student.

    Returns
    -------
    df : pd.DataFrame
      The corrected DataFrame after insertion of the mean grade
    arr : np.ndarray
          Row indices of the students that their new grades were generated
        """
        l = []

        for index, row in self.data.iterrows():
            df_qus = row[['q1','q2','q3','q4','q5']]
            if df_qus.isin(['nan']).any():

                df_qus = df_qus.replace('nan', np.nan).copy()
                print(f'old Row = {df_qus}')

                mean = df_qus.mean()
                array = df_qus.isin([np.nan]).values
                #l = array.tolist()
                #i_to_insert = [i for i, x in enumerate(l) if x]
                df_qus[array] = mean
                print(f'New Row = {df_qus}')

                l.append(index)
                self.data._set_value(index,['q1','q2','q3','q4','q5'],df_qus[['q1','q2','q3','q4','q5']])

        l = np.array(l)
        return self.data,l

            #print(index,row.q1)

    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
        """Calculates the average score of a subject and adds a new "score" column
        with it.

        If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
        score should be NA. Otherwise, the score is simply the mean of the other grades.
        The datatype of score is UInt8, and the floating point raw numbers should be
        rounded down.

        Parameters
        ----------
        maximal_nans_per_sub : int, optional
            Number of allowed NaNs per subject before giving a NA score.

        Returns
        -------
        pd.DataFrame
            A new DF with a new column - "score".
        """
        def ser_mean(ser,maximal_nans_per_sub: int = 1):

            ser = ser.replace('nan',np.nan )
            if ser.isna().sum() > maximal_nans_per_sub:
                return pd.NA
            return math.floor(ser.mean())
        df = self.data.copy()
        col = pd.Series(['q1', 'q2', 'q3', 'q4', 'q5'])
        df['score'] = df[col].apply(ser_mean,axis=1).astype('UInt8')
        return df












