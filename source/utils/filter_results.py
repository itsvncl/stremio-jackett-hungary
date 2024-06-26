import re

from utils.filter.language_filter import LanguageFilter
from utils.filter.max_size_filter import MaxSizeFilter
from utils.filter.quality_exclusion_filter import QualityExclusionFilter
from utils.filter.results_per_quality_filter import ResultsPerQualityFilter
from utils.filter.title_exclusion_filter import TitleExclusionFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)

quality_order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}


def sort_quality(item):
    return quality_order.get(item.quality, float('inf')), item.quality is None


def items_sort(items, config):
    if config['sort'] == "quality":
        return sorted(items, key=sort_quality)
    if config['sort'] == "sizeasc":
        return sorted(items, key=lambda x: int(x.size))
    if config['sort'] == "sizedesc":
        return sorted(items, key=lambda x: int(x.size), reverse=True)
    if config['sort'] == "qualitythensize":
        return sorted(items, key=lambda x: (sort_quality(x), -int(x.size)))
    return items

def filter_out_non_matching(items, season, episode):
    filtered_items = []
    for item in items:
        title = item.title.upper()
        season_pattern = r'S\d+'
        episode_pattern = r'E\d+'

        season_substrings = re.findall(season_pattern, title)
        season_substrings_len = len(season_substrings)
        if season_substrings_len > 0 and season_substrings_len != 2 and season not in season_substrings:
            continue
        
        if season_substrings_len == 2:
            season_num = int(season[1:])
            season_substrings[0] = int(season_substrings[0][1:])
            season_substrings[1] = int(season_substrings[1][1:])
            season_substrings.sort()
            
            if season_num < season_substrings[0] or season_num > season_substrings[1]:
                continue

        if season_substrings_len != 0:
            episode_substrings = re.findall(episode_pattern, title)
            episode_substrings_len = len(episode_substrings)
            if episode_substrings_len > 0 and episode_substrings_len != 2 and episode not in episode_substrings:
                continue
            
            if episode_substrings_len == 2:
                ep_num = int(episode[1:])
                episode_substrings[0] = int(episode_substrings[0][1:])
                episode_substrings[1] = int(episode_substrings[1][1:])
                episode_substrings.sort()
                
                if ep_num < episode_substrings[0] or ep_num > episode_substrings[1]:
                    continue

        filtered_items.append(item)

    return filtered_items


def filter_items(items, media, config):
    filters = {
        "languages": LanguageFilter(config),
        "maxSize": MaxSizeFilter(config, media.type),  # Max size filtering only happens for movies, so it
        "exclusionKeywords": TitleExclusionFilter(config),
        "exclusion": QualityExclusionFilter(config),
        "resultsPerQuality": ResultsPerQualityFilter(config)
    }

    # Filtering out 100% non matching for series
    logger.info(f"Item count before filtering: {len(items)}")
    if media.type == "series":
        logger.info(f"Filtering out non matching series torrents")
        items = filter_out_non_matching(items, media.season, media.episode)
        logger.info(f"Item count changed to {len(items)}")

    for filter_name, filter_instance in filters.items():
        try:
            logger.info(f"Filtering by {filter_name}: " + str(config[filter_name]))
            items = filter_instance(items)
            logger.info(f"Item count changed to {len(items)}")
        except Exception as e:
            logger.error(f"Error while filtering by {filter_name}", exc_info=e)
    logger.info("Finished filtering torrents")
    logger.info(f"Item count after filtering: {len(items)}")
    return items


def sort_items(items, config):
    if config['sort'] is not None:
        return items_sort(items, config)
    else:
        return items
