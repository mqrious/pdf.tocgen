from mamba import description, it, before
from fitzutils import ToCEntry
from pdftocgen.tocgen import merge_toc, auto_merge_toc

with description("merge_toc") as self:
    with it("merges basic consecutive entries within threshold"):
        entries = [
            ToCEntry(level=1, title="Chapter", pagenum=1, vpos=100.0),
            ToCEntry(level=1, title="One", pagenum=1, vpos=110.0),
            ToCEntry(level=1, title="Details", pagenum=1, vpos=200.0)
        ]
        # Threshold 15.0 should merge "Chapter" and "One" (diff 10.0)
        # but not "Details" (diff 90.0)
        merged = merge_toc(entries, threshold=15.0)
        
        assert len(merged) == 2
        assert merged[0].title == "Chapter One"
        assert merged[1].title == "Details"

    with it("does not merge entries on different pages"):
        entries = [
            ToCEntry(level=1, title="Chapter", pagenum=1, vpos=100.0),
            ToCEntry(level=1, title="One", pagenum=2, vpos=110.0)
        ]
        merged = merge_toc(entries, threshold=20.0)
        assert len(merged) == 2
        assert merged[0].title == "Chapter"
        assert merged[1].title == "One"

    with it("does not merge entries with different levels"):
        entries = [
            ToCEntry(level=1, title="Chapter", pagenum=1, vpos=100.0),
            ToCEntry(level=2, title="One", pagenum=1, vpos=110.0)
        ]
        merged = merge_toc(entries, threshold=20.0)
        assert len(merged) == 2
        assert merged[0].title == "Chapter"
        assert merged[1].title == "One"

    with it("merges multiple consecutive segments correctly"):
        entries = [
            ToCEntry(level=1, title="This", pagenum=1, vpos=100.0),
            ToCEntry(level=1, title="Is", pagenum=1, vpos=110.0),
            ToCEntry(level=1, title="A", pagenum=1, vpos=120.0),
            ToCEntry(level=1, title="Long", pagenum=1, vpos=130.0),
            ToCEntry(level=1, title="Title", pagenum=1, vpos=140.0)
        ]
        merged = merge_toc(entries, threshold=15.0)
        assert len(merged) == 1
        assert merged[0].title == "This Is A Long Title"

    with it("does not merge when threshold is zero"):
        entries = [
            ToCEntry(level=1, title="Chapter", pagenum=1, vpos=100.0),
            ToCEntry(level=1, title="One", pagenum=1, vpos=110.0)
        ]
        merged = merge_toc(entries, threshold=0.0)
        assert len(merged) == 2

with description("auto_merge_toc") as self:
    with it("merges based on font size from recipe"):
        # Based on user's manual calculation
        # Font size 20. Approx line height 20-30.
        # Threshold 3.0 * 20 = 60.
        entries = [
            ToCEntry(level=1, title="1", pagenum=23, vpos=91.25),
            ToCEntry(level=1, title="Making", pagenum=23, vpos=135.64), # diff 44.4
            ToCEntry(level=1, title="World", pagenum=23, vpos=164.44),  # diff 28.8
            ToCEntry(level=1, title="Next", pagenum=23, vpos=300.0)     # diff 135
        ]
        recipe_dict = {
            'heading': [
                {'level': 1, 'font': {'size': 20.0}}
            ]
        }
        
        merged = auto_merge_toc(entries, recipe_dict)
        
        assert len(merged) == 2
        assert merged[0].title == "1 Making World"
        assert merged[1].title == "Next"
