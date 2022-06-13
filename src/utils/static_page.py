from flask import render_template, make_response


def static_page(currentPage: str, template_path: str):
    """
    Boilerplate for a static page.
    """
    props = dict(
        currentPage=currentPage
    )
    response = make_response(render_template(
        template_path,
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'

    return response
