from collections import Counter
from operator import itemgetter
from sqlalchemy.sql import func
from app import db
from app.models import Vote

def irv():
    # IRV can result in a tie (e.g. final round has two candidates with 50%, or
    # three candidates with 33.3%, etc.) so we allow for a list of winners
    # Each round we remove the lowest percentage candidates by adding them to
    # this mask
    winners = {}
    removed = [-1]

    while not winners:
        top_noms = db.session.query(Vote.nominee).filter_by(ballot=1). \
                   filter(Vote.nominee.notin_(removed)). \
                   group_by(Vote.user).having(func.max(Vote.score)).all()

        votes = dict(Counter([n[0] for n in top_noms]))
        total_votes = sum(votes.values())
        percents = {nominee: float(num_votes) / total_votes
                    for nominee, num_votes in votes.iteritems()}

        max_nominee, max_percent = max(percents.iteritems(), key=itemgetter(1))

        # If a candidate has >50% of the votes they automatically are the sole
        # winner; if not, we have either tied or need to iterate again
        if max_percent > 0.5:
            winners[max_nominee] = max_percent
        else:
            min_percent = min(percents.values())
            all_nominees = set(percents.keys())
            min_nominees = {nominee for nominee, percent in
                            percents.iteritems() if percent == min_percent}

            # If all remaining nominees in this round have the same percent of
            # the votes, then we have tied and should return all current
            # nominees; otherwise we should remove the lowest candidates and
            # iterate
            if min_nominees == all_nominees:
                winners = {nom: min_percent for nom in all_nominees}
            else:
                removed.update(min_nominees)

    return winners
