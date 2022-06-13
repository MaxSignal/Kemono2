from flask import Blueprint, render_template, make_response, redirect, url_for, request

help_app = Blueprint('help_app', __name__)


@help_app.route('/')
def help():
    return redirect(url_for('help_app.faq'), 302)
    # props = dict(
    #     currentPage= 'help'
    # )
    # response = make_response(render_template(
    #     'help/list.html',
    #     props = props
    # ), 200)
    # response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    # return response


@help_app.get('/faq')
def faq():
    props = dict(
        currentPage='help'
    )
    response = make_response(render_template(
        'help/faq.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response

# @help_app.route('/posts')
# def posts():
#     props = dict(
#         currentPage= 'help'
#     )
#     response = make_response(render_template(
#         'help/posts.html',
#         props = props
#     ), 200)
#     response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
#     return response

# @help_app.route('/about')
# def about():
#     props = dict(
#         currentPage= 'help'
#     )
#     response = make_response(render_template(
#         'help/about.html',
#         props = props
#     ), 200)
#     response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
#     return response

# @help_app.route('/license')
# def license():
#     props = dict(
#         currentPage= 'help'
#     )
#     response = make_response(render_template(
#         'help/license.html',
#         props = props
#     ), 200)
#     response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
#     return response

# @help_app.route('/rules')
# def rules():
#     props = dict(
#         currentPage= 'help'
#     )
#     response = make_response(render_template(
#         'help/rules.html',
#         props = props
#     ), 200)
#     response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
#     return response
