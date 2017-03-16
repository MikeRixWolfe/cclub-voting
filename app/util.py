from collections import Counter
from operator import itemgetter
from sqlalchemy.sql import func
from app import db
from app.models import Vote

def irv(ballot_id, eligible):
    # IRV can result in a tie (e.g. final round has two candidates with 50%, or
    # three candidates with 33.3%, etc.) so we allow for a list of winners
    # Each round we remove the lowest percentage candidates by adding them to
    # this mask
    winners = {}
    removed = [-1]  # SQL optimization for query below (avoid not in $empty)

    while not winners:
        top_nominees = db.session.query(Vote.nominee).filter_by(ballot=ballot_id). \
                   filter(Vote.nominee.notin_(removed)). \
                   filter(Vote.nominee.in_(eligible)). \
                   group_by(Vote.user).having(func.max(Vote.score)).all()

        votes = dict(Counter([n[0] for n in top_nominees]))
        total_votes = sum(votes.values())
        percents = {nominee: float(num_votes) / total_votes
                    for nominee, num_votes in votes.iteritems()}

        max_nominee, max_percent = max(percents.iteritems(), key=itemgetter(1))

        # If a candidate has >50% of the votes they automatically are the sole
        # winner; if not, we have either tied or need to iterate again
        if len([nominee for nominee, score in percents.iteritems()
               if score == max_percent]) == 1:
            winners[max_nominee] = max_percent
        else:
            min_percent = min(percents.values())
            all_nominees = percents.keys()
            min_nominees = [nominee for nominee, percent in
                            percents.iteritems() if percent == min_percent]

            # If all remaining nominees in this round have the same percent of
            # the votes, then we have tied and should return all current
            # nominees; otherwise we should remove the lowest candidates and
            # iterate
            if min_nominees == all_nominees:
                winners = {nom: min_percent for nom in all_nominees}
            else:
                removed.extend(min_nominees)
                eligible = [nominee for nominee, score in percents.iteritems()
                            if nominee not in removed]

    return winners
