from fitz import Document
from typing import List, Dict, Optional
from fitzutils import ToCEntry
from .recipe import Recipe, extract_toc

def gen_toc(doc: Document, recipe_dict: dict) -> List[ToCEntry]:
    """Generate the table of content for a document from recipe

    Argument
      doc: a pdf document
      recipe_dict: the recipe dictionary used to generate the toc
    Returns
      a list of ToC entries
    """
    return extract_toc(doc, Recipe(recipe_dict))


def merge_toc(entries: List[ToCEntry],
              threshold: float = 0.0,
              thresholds_map: Optional[Dict[int, float]] = None) -> List[ToCEntry]:
    """Merge ToC entries that are close to each other.

    This is useful for handling multi-line headings that are recognized as
    separate entries.

    Argument
      entries: a list of ToC entries
      threshold: the vertical distance threshold for merging. If the distance
                 between two entries is smaller than this value, they will be
                 merged.
      thresholds_map: a dictionary mapping level to threshold. If provided,
                      it overrides the single threshold argument.
    Returns
      a list of ToC entries
    """
    if not entries:
        return []

    merged = []
    curr = entries[0]
    last_vpos = curr.vpos

    for next_entry in entries[1:]:
        # determine threshold
        if thresholds_map:
            t = thresholds_map.get(curr.level, threshold)
        else:
            t = threshold

        # check if we should merge
        # 1. must be on the same page
        # 2. must have the same level
        # 3. vpos must be available
        # 4. distance must be smaller than threshold
        if (curr.pagenum == next_entry.pagenum and
            curr.level == next_entry.level and
            last_vpos is not None and next_entry.vpos is not None and
            next_entry.vpos > last_vpos and
            (next_entry.vpos - last_vpos) <= t):
            # merge
            curr.title = f"{curr.title.strip()} {next_entry.title.strip()}"
            last_vpos = next_entry.vpos
        else:
            curr.title = curr.title.strip()
            merged.append(curr)
            curr = next_entry
            last_vpos = curr.vpos

    merged.append(curr)
    return merged


def auto_merge_toc(entries: List[ToCEntry], recipe_dict: dict) -> List[ToCEntry]:
    """Automatically merge ToC entries based on font size.

    Argument
      entries: a list of ToC entries
      recipe_dict: the recipe dictionary used to generate the toc
    Returns
      a list of ToC entries
    """
    recipe = Recipe(recipe_dict)
    sizes = {}
    for f in recipe.filters:
        if f.font.size and f.font.size > sizes.get(f.level, 0.0):
            sizes[f.level] = f.font.size

    # 3.0 seems to be a safe multiplier to cover most line spacings
    thresholds = {lvl: size * 3.0 for lvl, size in sizes.items()}
    
    return merge_toc(entries, thresholds_map=thresholds)
