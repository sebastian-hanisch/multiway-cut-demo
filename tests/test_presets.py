"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen; Permalink-Grenzen."""

import mwc_constants as C
import mwc_evaluation as ev
import mwc_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        assert preset["kind"] in C.KINDS, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.DEG_MIN <= preset["deg"] <= C.DEG_MAX and C.LINKS_MIN <= preset["links"] <= C.LINKS_MAX, name
        assert C.K_MIN <= preset["k"] <= C.K_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_the_first_preset_equals_the_default_settings_and_the_default_k():
    first = C.PRESETS[next(iter(C.PRESETS))]
    assert ev.Settings(**first) == ev.Settings() and first["k"] == C.DEFAULT_K


def test_setting_specs_cover_every_preset_key_and_every_choice_field_is_listed():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert {spec.url_param for spec in P.SETTING_SPECS.values()} == {"kind", "n", "deg", "links", "seed", "k"}
    assert set(P.CHOICES) == {"kind_select"} and P.CHOICES["kind_select"] == C.KINDS


def test_every_kind_has_a_name_a_help_text_and_a_regler_note():
    assert set(C.KIND_NAMES) == set(C.KIND_HELP) == set(C.KIND_REGLER) == set(C.KINDS)


def test_the_experiment_grid_uses_only_known_kinds_and_sizes_inside_the_limits():
    assert all(kind in C.KINDS and kind != "tight" for kind, _deg in C.EX_KINDS)
    assert C.N_MIN <= C.EX_N <= C.BRUTE_N and C.EX_KCUT_N <= C.BRUTE_KCUT_N <= C.BRUTE_N and C.EX_BIG_N > C.BRUTE_N and C.EX_BIG_N <= C.N_MAX and int(C.EX_BIG_N ** 0.5) ** 2 == C.EX_BIG_N
    assert int(C.EX_KCUT_N ** 0.5) ** 2 == C.EX_KCUT_N and C.EX_BIG_SEEDS <= len(C.SWEEP_SEEDS) and all(C.K_MIN <= k <= C.K_MAX for k in C.EX_KS + C.EX_KCUT_KS + C.TIGHT_KS if k <= C.K_MAX)
    assert C.TIGHT_KS[0] == C.K_MIN and len(C.COLOR_TERMINALS) > C.K_MAX


def test_the_enumeration_limits_match_the_presets():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert (a.exact is not None) == (a.n <= C.BRUTE_N) and (a.kexact is not None) == (a.n <= C.BRUTE_KCUT_N), name
    assert max(ev.analyse(ev.Settings(**p)).n for p in C.PRESETS.values()) > C.BRUTE_N
