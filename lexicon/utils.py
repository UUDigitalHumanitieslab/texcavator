"""Utility functions for lexicon"""


from models import LexiconItem


def get_query(lexicon_id):
    """Returns the query stored for a lexicon id and an appropriate error 
    message if the query cannot be retrieved.
    """
    query = None
    response = None

    try:
        li = LexiconItem.objects.get(pk=lexicon_id)
        query = li.query
    except LexiconItem.DoesNotExist:
        msg = "Lexicon with id %s cannot be found." % lexicon_id
        response = json_response_message('error', msg)
    except DatabaseError:
        response = json_response_message('error', 
                'Database error while retrieving lexicon')

    if not query and not response: 
        response = json_response_message('error', 'No query found.')

    return query, response
