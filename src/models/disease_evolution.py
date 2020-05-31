import numpy as np
from scipy.stats import truncnorm


def sample_truncated_norm(clip_low, clip_high, mean, std):
    a, b = (clip_low - mean) / std, (clip_high - mean) / std
    return int(truncnorm.rvs(a, b, mean, std))


def incubation(clip_low=2, clip_high=15, mean=6, std=3):
    return sample_truncated_norm(clip_low, clip_high, mean, std)


def onset_to_hosp_or_asymp(clip_low=2, clip_high=21, mean=6.2, std=4.3):
    return sample_truncated_norm(clip_low, clip_high, mean, std)


def hospitalization_to_removed(clip_low=2, clip_high=32, mean=8.6, std=6.7):
    return sample_truncated_norm(clip_low, clip_high, mean, std)


def needs_hospitalization(age):
    # https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf
    if age <= 9:
        return np.random.random() <= 0.001
    if age <= 19:
        return np.random.random() <= 0.003
    if age <= 29:
        return np.random.random() <= 0.012
    if age <= 39:
        return np.random.random() <= 0.032
    if age <= 49:
        return np.random.random() <= 0.049
    if age <= 59:
        return np.random.random() <= 0.102
    if age <= 69:
        return np.random.random() <= 0.166
    if age <= 79:
        return np.random.random() <= 0.243
    return np.random.random() <= 0.273


def hospitalized_needs_ICU(age):
    # https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf
    if age <= 9:
        return np.random.random() <= 0.05
    if age <= 19:
        return np.random.random() <= 0.05
    if age <= 29:
        return np.random.random() <= 0.05
    if age <= 39:
        return np.random.random() <= 0.05
    if age <= 49:
        return np.random.random() <= 0.063
    if age <= 59:
        return np.random.random() <= 0.122
    if age <= 69:
        return np.random.random() <= 0.274
    if age <= 79:
        return np.random.random() <= 0.432
    return np.random.random() <= 0.709
