"""Publisher metadata shared by the initial review and incremental sync."""
from html import unescape
import re
import unicodedata


def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', unescape(text))).strip()


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', clean(text)).casefold() if c.isalnum())


JOURNALS = {
    'IEEE Transactions on Parallel and Distributed Systems': 'IEEE TPDS',
    'IEEE/ACM Transactions on Networking': 'IEEE/ACM ToN',
    'IEEE Transactions on Mobile Computing': 'IEEE TMC',
    'IEEE Transactions on Computers': 'IEEE TC',
    'IEEE Journal on Selected Areas in Communications': 'IEEE JSAC',
    'IEEE Transactions on Services Computing': 'IEEE TSC',
    'IEEE Transactions on Sustainable Computing': 'IEEE TSUSC',
    'IEEE Transactions on Cloud Computing': 'IEEE TCC',
    'IEEE Transactions on Vehicular Technology': 'IEEE TVT',
    'IEEE Transactions on Big Data': 'IEEE TBD',
    'IEEE Communications Surveys & Tutorials': 'IEEE COMST',
    'IEEE Transactions on Multimedia': 'IEEE TMM',
    'IEEE Transactions on Automation Science and Engineering': 'IEEE TASE',
    'IEEE Transactions on Industrial Electronics': 'IEEE TIE',
    'IEEE Transactions on Computational Social Systems': 'IEEE TCSS',
    'IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems': 'IEEE TCAD',
    'IEEE Transactions on Geoscience and Remote Sensing': 'IEEE TGRS',
    'IEEE Transactions on Network Science and Engineering': 'IEEE TNSE',
    'IEEE Internet of Things Journal': 'IEEE IoT Journal',
    'ACM Transactions on Sensor Networks': 'ACM TOSN',
    'ACM Transactions on Multimedia Computing, Communications, and Applications': 'ACM TOMM',
    'Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies': 'ACM IMWUT',
    'Proceedings of the VLDB Endowment': 'PVLDB',
    'CCF Transactions on High Performance Computing': 'CCF THPC',
    'Concurrency and Computation: Practice and Experience': 'CCPE',
    'Engineering Applications of Artificial Intelligence': 'EAAI',
    'Expert Systems with Applications': 'ESWA',
    'Frontiers of Computer Science': 'FCS',
    'Big Data Mining and Analytics': 'BDMA',
    'APSIPA Transactions on Signal and Information Processing': 'APSIPA TSIP',
}


def venue_fields(work):
    containers = [clean(v) for v in work.get('container-title') or []]
    # A book series is not the conference name. Crossref also registers the volume title.
    venue = containers[-1] if len(containers) > 1 and work.get('type') == 'book-chapter' else (containers[0] if containers else '')
    if venue in JOURNALS:
        return venue, JOURNALS[venue]
    conference_names = {
        'Principles and Practice of Parallel Programming': 'PPoPP',
        'International Conference on Parallel Processing': 'ICPP',
        'International Conference on Supercomputing': 'ICS',
        'International Conference on Multimedia Retrieval': 'ICMR',
        'ACM Special Interest Group on Data Communication': 'SIGCOMM',
        'International Conference on Information and Knowledge Management': 'CIKM',
        'International on Conference on Information and Knowledge Management': 'CIKM',
        'International Symposium on Quality of Service': 'IWQoS',
        'Asia-Pacific Workshop on Networking': 'APNet',
        'International Conference on Mobile Systems, Applications, and Services': 'MobiSys',
        'International Conference on Mobile Computing and Networking': 'MobiCom',
        'International Symposium on Mobile Ad Hoc Networking and Computing': 'MobiHoc',
        'ACM SIGMETRICS International Conference': 'SIGMETRICS',
        'Service-Oriented Computing': 'ICSOC',
        'Security, Privacy, and Anonymity in Computation, Communication, and Storage': 'SpaCCS',
        'Cyberspace Safety and Security': 'CSS',
        'Advances in Services Computing': 'APSCC',
        'Database Systems for Advanced Applications': 'DASFAA',
        'Euro-Par': 'Euro-Par',
        'Knowledge Science, Engineering and Management': 'KSEM',
        'Advanced Intelligent Computing Technology and Applications': 'ICIC',
        'ECAI': 'ECAI',
        'International Conference on Advanced Cloud and Big Data': 'CBD',
        'International Conference on Joint Cloud Computing': 'JCC',
        'International Conference on Big Data, Artificial Intelligence and Risk Management': 'ICBAR',
    }
    for name, label in conference_names.items():
        if name.casefold() in venue.casefold():
            return venue, label
    if 'INFOCOM' in venue:
        return venue, 'INFOCOM'
    # Acronyms explicitly supplied by the publisher, not inferred ranking labels.
    acronyms = re.findall(r'\(([A-Za-z][A-Za-z0-9/-]{1,40})(?:\s+\d{4})?\)', venue)
    label = acronyms[-1] if acronyms else venue
    return venue, label


def metadata(work, checked_on, title=None):
    venue, label = venue_fields(work)
    if not venue or not work.get('DOI'):
        raise ValueError('Publisher DOI and venue are required')
    doi = work['DOI'].lower()
    return {'title': clean(title or (work.get('title') or [''])[0]),
            'venue': venue, 'label': label, 'doi': doi,
            'link': 'https://doi.org/' + doi,
            'verification': 'Crossref publisher deposit', 'checkedOn': checked_on}
