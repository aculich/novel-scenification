# Novel Scene Analysis Project

This repository contains tools for analyzing scenes and tags in literary texts, particularly focusing on the evolution of scenic techniques in English novels from 1788-1828.

This repository supports the following paper, currently in preprint form being prepared for publication:

> # Scenification of the Novel in the Time of Jane Austen
>
> Authors: Nicholas Paige^1,*; Aaron Culich^2
>
> - ^1 University of California, Department of French, Berkeley CA 94530-2580 USA  
> - ^2 University of California, Eviction Research Network, Berkeley CA 94530 USA
>
> ## Abstract
>
> This paper presents a study of the evolving use of scenes in the English novel circa 1800. The distinction between summary and scene has been a basic one in classical narratology, but comparatively little research exists on the historical development of scenic narrative techniques. Although quantitative methods have identified growth in textual features that may be expected to be linked to changes in scenic narration, the typical bag-of-words approach has limited understanding of how techniques perceptible to human readers may change over time. Our approach uses a hierarchical tagging schema to annotate scene types and their internal components to assist in quantifying scenic architecture. The project described uses BeautifulSoup4 and custom Python scripts and future analysis will integrate computational tools such as BookNLP with custom scene annotations in order to understand the evolution of narrative techniques.
>
> ## Keywords
>
> Narratology, novel, fiction, scene, summary

## Tag Schema

The hierarchical tagging schema is comprised of primary scene category tags and nested component tags. Then we process the tagged text using BeautifulSoup4 and custom Python scripts (`count_tags.py` available in our github repository) to quantify:
   - Frequency and word count of each scene type
   - Hierarchical relationships between primary and component tags

The HTML files are tagged with a custom schema that identifies different scene types:

### Primary Scene Tags
- `<SceneDia>`: Dialogue-dominant scenes where character speech drives narrative progression
- `<SceneAction>`: Action-focused scenes depicting physical events or movements
- `<SceneQuasi>`: Transitional scenes blending scenic and summary elements
- `<ScenePerception>`: Scenes focused on character perception and sensory experience

### Component Tags
Within each scene type, we track:
- `<Dia>, <DiaM>, <DiaQ>`: Direct dialogue with varying attributions
- `<Trigger>`: Temporal or spatial anchors that signal scene transitions
- `<M>`: Markers denoting speech attribution or narrative framing
- `<FID>`: Free indirect discourse elements

## Data & Code Overview

The project analyzes manually tagged HTML files to track the development of scenic techniques in novels. It processes these files to count tags, calculate word counts within different scene types, and analyze hierarchical relationships between tags.

### Contents

- `count_tags.py`: The main script for processing tagged HTML files
- `data/input/`: Directory containing HTML files with manual tagging
- `data/counts/`: Directory where CSV output files are stored
- [`data/tag_counts_summary.xlsx`](https://github.com/aculich/novel-scenification/raw/refs/heads/main/data/tag_counts_summary.xlsx): Excel summary file of all tag counts and analysis (direct download link)

### Requirements

Required Python packages:
```
beautifulsoup4>=4.9.3
pandas>=1.3.0
openpyxl>=3.0.7
```

### Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the tag counting script:
   ```
   python count_tags.py
   ```

3. The script will:
   - Process all HTML files in `data/input/`
   - Generate CSV files with tag counts in `data/counts/`
   - Create a summary Excel file at `data/tag_counts_summary.xlsx`

## Tag Counts Summary

[View complete tag counts summary](https://github.com/aculich/novel-scenification/raw/refs/heads/main/data/tag_counts_summary.xlsx)

| Sheet | Total_Tags | Total_Words | Chapter_Count | SceneAction_Count | SceneAction_Words | SceneDia_Count | SceneDia_Words | Dialogue_Count | Dialogue_Words |
|-------|------------|-------------|---------------|------------------|------------------|----------------|----------------|----------------|----------------|
| [1828 Loudon 1_4_11057 Erin](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Loudon%201_4_11057%20Erin.html) | 307 | 14797 | 4 | 3 | 6231 | 3 | 3284 | 28 | 1191 |
| [1828 Colburn 1_2_13824](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Colburn%201_2_13824.html) | 238 | 13695 | 2 | 4 | 4415 | 3 | 1807 | 12 | 540 |
| [1788 Anon Helena 1_20_12500](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Helena%201_20_12500.html) | 181 | 12157 | 20 | 3 | 13702 | 3 | 1713 | 1 | 11 |
| [1788 Anon Amicable Q 1_3_13234 final](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Amicable%20Q%201_3_13234%20final.html) | 327 | 13130 | 3 | 1 | 1259 | 5 | 7592 | 64 | 3657 |
| [1788 Anon Oswald Castle 1_6_13800 Erin](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html) | 427 | 13861 | 7 | 3 | 3550 | 6 | 6802 | 25 | 433 |
| [1788 Wollstonecraft 1_16_12447](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Wollstonecraft%201_16_12447.html) | 151 | 12667 | 14 | 1 | 316 | 2 | 1553 | 3 | 57 |
| [1808 Norris 1_7_12512](https://github.com/aculich/novel-scenification/blob/main/data/input/1808%20Norris%201_7_12512.html) | 329 | 12416 | 7 | 4 | 3899 | 6 | 3035 | 50 | 1089 |
| [1828 Cunningham 1_2_12439](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Cunningham%201_2_12439.html) | 264 | 12059 | 2 | 1 | 5912 | 1 | 6042 | 2 | 174 |
| [1788 Anon Amicable Q 1_3_13234](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Amicable%20Q%201_3_13234.html) | 327 | 13247 | 3 | 1 | 1269 | 5 | 7656 | 64 | 3686 |
| [1808 Montague 1_2_12825](https://github.com/aculich/novel-scenification/blob/main/data/input/1808%20Montague%201_2_12825.html) | 141 | 12701 | 2 | 2 | 2373 | 4 | 3439 | 3 | 127 |
| [1828 Bray Protestant 1_2_14300 Erin](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Bray%20Protestant%201_2_14300%20Erin.html) | 441 | 13721 | 2 | 0 | 0 | 2 | 12295 | 1 | 95 |
| [1808 Anon_Master Passion 1_6_11555](https://github.com/aculich/novel-scenification/blob/main/data/input/1808%20Anon_Master%20Passion%201_6_11555.html) | 271 | 11527 | 6 | 4 | 3207 | 6 | 3919 | 80 | 2477 |
| [1828 Harvey 1_3_13500](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Harvey%201_3_13500.html) | 280 | 12999 | 3 | 2 | 4041 | 3 | 8195 | 12 | 556 |


## Scene Samples

[View complete samples analysis](data/SAMPLES.md)

# Scene Samples

This document contains particularly rich examples of scene markup from each text, showing complex interactions between different types of scenes and their components. For each scene, we show interesting excerpts including openings, transitions, rich dialog sections, and endings.

## [1828 Bray Protestant 1_2_14300 Erin.html](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Bray%20Protestant%201_2_14300%20Erin.html)

### Complex Scenedia (Lines 60-484)

**Location:** [Lines 60-484](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Bray%20Protestant%201_2_14300%20Erin.html#L60-L484)

**Complexity Metrics:**
- Unique tag types: 18
- Total nested tags: 264
- Word count: 7650
- Tag types present: arrivaldeparture, authorwe, blend, chapmarker, chnameexternal, chnameintro, chnonameexternal, departurearrival, descriptor, diam, diaq, footnote, i, m, quotedlit, quotedtext, speechimagined, trigger

**Interesting Excerpts:**

*Scene Transition:* [Lines 60-484](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Bray%20Protestant%201_2_14300%20Erin.html#L60-L484)
```html
<scenedia><trigger>One morning</trigger>, whilst Wilford was preparing to take his usual walk round the village of Wellminster, he was surprised by the sudden entrance of his old and faithful servant, Abel

#10#

Allen, who appeared greatly disturbed, and, coming up to his master, said in a most agitated manner, <diaq>"Thornton is coming!"</diaq>
<diam>"Thornton!" <m>exclaimed Wilford</m>, "Thornton! and to <i>my</i> house?"</diam>
<diam>"Ay, Thornton is coming, sure enough," <m>replied Abel</m>; "and I don’t think he is coming alone either, for I saw him standing in the green lane near Gammer Plaise’s cottage, with a couple of fellows of his own kidney, and I do think there was more of them still behind. But who cares for that?" added the old servingman stoutly; "shall I knock him down, or shut the door in his face?"</diam>
<diam>"Do neither," <m>replied Wilford;</m> "I will not refuse to see him; although, if I did so refuse, I could find a warrant for it in my own breast. Yet, I will see him. Show him into the little oak parlour, and tell your mistress, Dame Alice, what sort of a visitor we are like to have. I will prepare my mind to meet that man, if I can, with composure."</diam>

#11#


<arrivaldeparture>Abel departed</arrivaldeparture>, to obey the instructions of his master; whilst Wilford, who appeared extremely affected by the very mention of Thornton's name, paced up and down the room with an agitation of manner that was rarely seen in a man of so mild and patient a temper. <blend>He then descended</blend> to the oak parlour, where he found his wife (who had been warned by Abel of Thornton’s approach) busily engaged in putting several things away in a closet.

<diam>"Alice," <m>said Wilford</m>, “you have removed it; bring the book back again, and lay it open, as it was, upon the table.”</diam>
<diam>"Nay, do not bid me," <m>replied his wife in an imploring tone</m>; "do not bid me; consider what it is."</diam>
<diam>"I do so," <m>answered Wilford</m>, "and therefore I command you to obey me. Shall I fear to have the service to my God in my mother tongue upon my table, because Thornton, the Suffragan Bishop of Dover, is coming to my house? Shall I deny my Master before His

#12#

enemies, because they are <i>my</i> enemies too? Thank God, sinner as I am, I can meet Thornton with a clear conscience. Bring back the book this moment; and what have you done with Luther <i>De Captivitate Babylonica?</i>”</diam>
<diam>"Oh do not make me bring <i>that</i> book, I conjure you," <m>said Alice, wringing her hands</m>, "If you do, you are a lost man, though Cardinal Pole himself should plead for you. Be content, I have put t...
```

*Scene Ending:* [Lines 60-484](https://github.com/aculich/novel-scenification/blob/main/data/input/1828%20Bray%20Protestant%201_2_14300%20Erin.html#L60-L484)
```html
<scenedia><trigger>One morning</trigger>, whilst Wilford was preparing to take his usual walk round the village of Wellminster, he was surprised by the sudden entrance of his old and faithful servant, Abel

#10#

Allen, who appeared greatly disturbed, and, coming up to his master, said in a most agitated manner, <diaq>"Thornton is coming!"</diaq>
<diam>"Thornton!" <m>exclaimed Wilford</m>, "Thornton! and to <i>my</i> house?"</diam>
<diam>"Ay, Thornton is coming, sure enough," <m>replied Abel</m>; "and I don’t think he is coming alone either, for I saw him standing in the green lane near Gammer Plaise’s cottage, with a couple of fellows of his own kidney, and I do think there was more of them still behind. But who cares for that?" added the old servingman stoutly; "shall I knock him down, or shut the door in his face?"</diam>
<diam>"Do neither," <m>replied Wilford;</m> "I will not refuse to see him; although, if I did so refuse, I could find a warrant for it in my own breast. Yet, I will see him. Show him into the little oak parlour, and tell your mistress, Dame Alice, what sort of a visitor we are like to have. I will prepare my mind to meet that man, if I can, with composure."</diam>

#11#


<arrivaldeparture>Abel departed</arrivaldeparture>, to obey the instructions of his master; whilst Wilford, who appeared extremely affected by the very mention of Thornton's name, paced up and down the room with an agitation of manner that was rarely seen in a man of so mild and patient a temper. <blend>He then descended</blend> to the oak parlour, where he found his wife (who had been warned by Abel of Thornton’s approach) busily engaged in putting several things away in a closet.

<diam>"Alice," <m>said Wilford</m>, “you have removed it; bring the book back again, and lay it open, as it was, upon the table.”</diam>
<diam>"Nay, do not bid me," <m>replied his wife in an imploring tone</m>; "do not bid me; consider what it is."</diam>
<diam>"I do so," <m>answered Wilford</m>, "and therefore I command you to obey me. Shall I fear to have the service to my God in my mother tongue upon my table, because Thornton, the Suffragan Bishop of Dover, is coming to my house? Shall I deny my Master before His

#12#

enemies, because they are <i>my</i> enemies too? Thank God, sinner as I am, I can meet Thornton with a clear conscience. Bring back the book this moment; and what have you done with Luther <i>De Captivitate Babylonica?</i>”</diam>
<diam>"Oh do not make me bring <i>that</i> book, I conjure you," <m>said Alice, wringing her hands</m>, "If you do, you are a lost man, though Cardinal Pole himself should plead for you. Be content, I have put t...
```

## [1788 Anon Oswald Castle 1_6_13800 Erin.html](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html)

### Complex Sceneaction (Lines 7-23)

**Location:** [Lines 7-23](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L7-L23)

**Complexity Metrics:**
- Unique tag types: 9
- Total nested tags: 67
- Word count: 2177
- Tag types present: authorwe, dia, diainset1p, diam, diaq, exclamation, i, m, reportedspeechquotes

**Interesting Excerpts:**

*Scene Opening:* [Lines 339-358](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L339-L358)
```html
<sceneaction>The next morning was spent in receiving visitors, who left them only time to prepare for the play, to which they had engaged to go with the Marchmonts, some time before; places were taken in the stage-box, and Sophia’s dress was remarkably elegant; she looked beautifully; the Marchmonts called for them, and she stepped into the carriage with more than usual vivacity. Lord Sandford was their only <i>escorte</i>
```

*Scene Ending:* [Lines 339-358](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L339-L358)
```html
<sceneaction>The next morning was spent in receiving visitors, who left them only time to prepare for the play, to which they had engaged to go with the Marchmonts, some time before; places were taken in the stage-box, and Sophia’s dress was remarkably elegant; she looked beautifully; the Marchmonts called for them, and she stepped into the carriage with more than usual vivacity. Lord Sandford was their only <i>escorte</i>, who was under an engagement for part of the evening, which would oblige him to

#65#

leave them when they were seated; but he promised to return before they would wish to leave the house. The play was one of Mrs. Cowley’s excellent comedies, and the third act was begun, which engaged all Sophia’s attention, when the audience were suddenly alarmed by the cry of <reportedspeechquotes>"Fire;"</reportedspeechquotes> the theatre was instantly in confusion, and the audience, by attempting to make their way out, rendered the scene still more frightful. --- Screams of terror and distress, -— the bursting open of doors, -- oaths and supplications, -- mixed in one dreadful tumult, terrified Sophia to agony; she jumped immediately over the benches behind her, and opening the door of the box, <exclamation>rushed instantly into the lobby!</exclamation> -— Here her situation was indeed frightful: encompassed by a crowd of people, who regarded only themselves, she vainly supplicated assistance; at length, her elegant figure attracting the attention of a party of young men, whose licentiousness, not

#66#

even the horror of the moment could repress; they seized her hand, and said they would protect her: the terrible imprecations they used to each other, awakened her to all the misery of her state, and the sound of protection, which had at first a little relieved her, from them, was even more dreadful than remaining unassisted. <diam>"No, no," <m>she exclaimed, endeavouring to disengage herself from them,</m> "suffer me to return to my friends, and I will share their fate."</diam> <diam>"We are your friends," <m>said they,</m> "and we will protect you."</diam> In saying this, they endeavoured to force her forward; the alarm had by this time ceased, and the lobby was almost empty: observing this, she hastily replied, <diaq>"No, there is no occasion, I thank you, gentlemen, the danger is over, and I will return to my party."</diaq> To this she received no answer, but an insolent laugh, some impertinent speeches to each other, and a continued effort to oblige her to go

#67#

with them. Wresting herself violently from their hold, she exclaimed, <diaq>"Unhand me, gentlemen, I will not go with you.”</diaq> A gentleman advancing, used some menacing language to these insolent fellows -— S...
```

### Complex Scenedia (Lines 29-37)

**Location:** [Lines 29-37](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L29-L37)

**Complexity Metrics:**
- Unique tag types: 12
- Total nested tags: 105
- Word count: 2310
- Tag types present: arrivaldeparture, blend, chapmarker, chaptitle, dia, diainset1p, diam, diaq, i, m, quotedlit, speechimangined

**Interesting Excerpts:**

*Scene Opening:* [Lines 405-424](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L405-L424)
```html
<scenedia>Sophia met her with repeated thanks for the kindness of her visit, which she said was perfectly consistent with the goodness she had shewn her the night before. —- They sat down together, Lady Helen still retained Sophia’s hand in her own, and looked on her as if she had said <speechimangined>"Have we not been acquainted these twelve months."</speechimangined>
```

*Scene Ending:* [Lines 405-424](https://github.com/aculich/novel-scenification/blob/main/data/input/1788%20Anon%20Oswald%20Castle%201_6_13800%20Erin.html#L405-L424)
```html
<scenedia>Sophia met her with repeated thanks for the kindness of her visit, which she said was perfectly consistent with the goodness she had shewn her the night before. —- They sat down together, Lady Helen still retained Sophia’s hand in her own, and looked on her as if she had said <speechimangined>"Have we not been acquainted these twelve months."</speechimangined> Sophia also, gazed on her, and found a form, if not perfectly beautiful, perhaps more agreeable than if it had been so: her eyes expressed every thought, and as they were her most lively feature, so they scarcely allowed you to think on any other: she was lower

#80#

in stature than Sophia, but the graces of her person prevented her from being insignificant. In short, she had just that kind of elegant attraction which wins the heart without consulting, or rather before it is possible to consult the reasons. They entered immediately into a very friendly conversation; and Sophia said, <diaq>“I trust, Lady Helen, you will not mortify me so cruelly, as just to shew me there exists a person so valuable as yourself, and then withdraw her from my society: will you add to the obligations I already feel half uneasy under, that of allowing me to see you often."</diaq> <diam>"On one condition;" <m>replied Lady Helen, smiling.</m></diam> <diam>“Name it;” <m>answered Sophia.</m></diam> <dia>“It is that you will not ever again mention, that horrid word <i>obligations</i>; if you do, I shall think you wish to remind <i>me</i> of those I owe <i>you</i> for admitting me; and, like you, I am very proud, and <i>hate to be obliged</i>.”</dia> Sophia returned her smile, and in the same tone promised

#81#

implicit obedience. <diainset1p>"My time," <m>said Lady Helen</m>, "while my father is out of town, is quite at my own disposal; and I find already, that I shall think most of that mispent, which is not passed with you: when my father is at home, I must dedicate a large part of every day to him. It is remarkabable enough," <m>added she,</m> “that but yesterday morning, I was saying to my brother <diaq>'I hear a great deal of Lady Sophia Woodville, I wish we could be introduced to her; but as we are unacquainted with Lord Marchmont’s family and most of those she visits, I fear it will not be easy.’</diaq> <diam>‘Oh,' <m>said he, smiling,</m> 'do not wish that for my sake, Helen, for I am told she is so extremely lovely, no man can withstand the power of her charms, and I wish to keep my heart awhile.'</diam>"</diainset1p> Sophia felt herself excessively confused at this recital, and with some difficulty said, <diaq>"Your Brother is by this time undeceived, if indeed, he ever <i>thought</i> thus."</diaq> Lady...
```

...

[View all scene samples](data/SAMPLES.md)
