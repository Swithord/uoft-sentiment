from flask import Flask, jsonify, request
import pandas as pd


def create_app():
    app = Flask(__name__)
    df = pd.read_csv('uoft_course_sentiments_small.csv', index_col=0)
    averages_df = df[['course','positive_sentiment','negative_sentiment']].groupby('course').mean().reset_index()
    averages_df['positive_rank'] = averages_df['positive_sentiment'].rank(ascending=False)
    averages_df['negative_rank'] = averages_df['negative_sentiment'].rank(ascending=False)

    @app.route('/courses')
    def courses():
        return jsonify(df['course'].unique().tolist())

    @app.route('/sentiments/')
    def sentiments():
        course = request.args.get('course')
        course_df = df[df['course'] == course]
        overall_positive = averages_df[averages_df['course'] == course]['positive_sentiment'].values[0]
        overall_negative = averages_df[averages_df['course'] == course]['negative_sentiment'].values[0]
        positive_rank = averages_df[averages_df['course'] == course]['positive_rank'].values[0]
        negative_rank = averages_df[averages_df['course'] == course]['negative_rank'].values[0]
        total_number_of_courses = averages_df.shape[0]
        most_negative = course_df['negative_sentiment'].idxmax()
        most_positive = course_df['positive_sentiment'].idxmax()
        df_list = []
        for year, year_df in course_df.groupby('year'):
            year_positive = year_df['positive_sentiment'].mean()
            year_negative = year_df['negative_sentiment'].mean()
            df_list.append({
                'year': year,
                'amount': year_df.shape[0],
                'positive_sentiment': year_positive,
                'negative_sentiment': year_negative
            })
        yearly_sentiments = pd.DataFrame(df_list)

        return jsonify({
            'course': course,
            'overall_positive': overall_positive,
            'overall_negative': overall_negative,
            'positive_rank': positive_rank,
            'negative_rank': negative_rank,
            'rank_out_of': total_number_of_courses,
            'yearly_sentiments': yearly_sentiments.to_dict('list'),
            'most_negative': {
                'text': df.loc[most_negative, 'text'],
                'year': int(df.loc[most_negative, 'year']),
            },
            'most_positive': {
                'text': df.loc[most_positive, 'text'],
                'year': int(df.loc[most_positive, 'year']),
            }
        })

    @app.route('/ranking/')
    def ranking():
        rank_type = request.args.get('type')
        if rank_type == 'positive':
            # we want the format to be course: rank
            return jsonify({course: rank for course, rank in zip(averages_df['course'], averages_df['positive_rank'])})
        elif rank_type == 'negative':
            return jsonify({course: rank for course, rank in zip(averages_df['course'], averages_df['negative_rank'])})
        else:
            return jsonify({'error': 'Invalid rank type'})

    return app

