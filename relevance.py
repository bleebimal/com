import pandas as pd


def revelance_calculate(filePath, input, val1, val2):

    df = pd.read_csv(filePath)

    if(val1 == 0):
        val1 = 100
    if(val2 == 0):
        val2 = 300

    keywords = input.split(' OR ')
    print(keywords, filePath, val1, val2)
    # print(df)

    if input == "":
        # 100 conditional values
        set1 = df.sort_values(by='Cited By (3 Years)',
                              ascending=False).head(val1).reset_index()
        # print(set1)

        temp_merge = pd.concat([df, set1])
        temp_set = temp_merge.drop_duplicates(
            subset='Publication Number', keep=False, inplace=False)

        # print(temp_set)

        set2 = temp_set.sample(val2)  # Random 200 values
        # print(set2)

        frames1 = [set1, set2]

        to_export = pd.concat(
            [df1.append(pd.Series(' '), ignore_index=True) for df1 in frames1])

        to_export.insert(0, 'Notes', '')
        to_export.insert(0, 'Relevancy Code', '')
        return(to_export)  # to be exported if empty

    else:
        set1 = df.sort_values(by='Cited By (3 Years)', ascending=False).head(
            val1).reset_index()  # 100 conditional values
        # print(set1)

        temp_merge = pd.concat([df, set1])
        temp_set = temp_merge.drop_duplicates(
            subset='Publication Number', keep=False, inplace=False)

        # print(temp_set)

        set2 = temp_set.sample(val2)  # Random 200 values
        # print(set2)

        final_set = pd.concat([set1, set2])
        # print(final_set)

        final_set["Token"] = final_set['Title'].apply(lambda x: 1 if any(i in x for i in keywords) else 0) | \
            final_set['Abstract'].apply(lambda x: 1 if any(i in x for i in keywords) else 0) | \
            final_set['First Claim'].apply(
                lambda x: 1 if any(i in x for i in keywords) else 0)

        # print(final_set)
        match = final_set[final_set['Token'] == 1]
        match_final = match.drop(['Token', 'index'], 1)

        unmatch = final_set[final_set['Token'] == 0]
        unmatch_final = unmatch.drop(['Token', 'index'], 1)

        frames1 = [match_final, unmatch_final]
    # with open(fname, mode='a+') as f:
    #     for df1 in frames1:
    #         df1.to_csv(fname, mode='a', header = f.tell() == 0)
    #         f.write('\n')

        to_export = pd.concat(
            [df1.append(pd.Series(' '), ignore_index=True) for df1 in frames1])

        for key, row in to_export.iterrows():
            if row['Publication Number'] == ' ':
                to_export.loc[key+1] = pd.Series('Unmatch')

        to_export.insert(0, 'Notes', '')
        to_export.insert(0, 'Relevancy Code', '')
        return(to_export)  # to be exported if not empty


# to_export.to_csv("out.csv", index=False)
