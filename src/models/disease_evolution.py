import numpy as np
from scipy.stats import truncnorm


def sample_truncated_norm(size, clip_low, clip_high, mean, std):
    """
    Given a range (a,b), returns the truncated norm
    """
    a, b = (clip_low - mean) / std, (clip_high - mean) / std
    return truncnorm.rvs(a, b, mean, std, size=size).astype(int)


def incubation(size, clip_low=2, clip_high=14.9, mean=5.6, std=2.8):
    """
    Returns the incubation time in days within range(clip_low, clip_high),
    of a truncated_norm(mean, std).
    """
    return sample_truncated_norm(size, clip_low, clip_high, mean, std)


def onset_to_hosp_or_asymp(size, clip_low=2, clip_high=21.1, mean=6.2, std=4.3):
    """
    Returns the time for someone to either get removed or hospitalized 
    in days within range(clip_low, clip_high),
    of a truncated_norm(mean, std).
    """
    return sample_truncated_norm(size, clip_low, clip_high, mean, std)


def hospitalization_to_removed(size, clip_low=2, clip_high=32.6, mean=8.6, std=6.7):
    """
    Returns the time for someone to either get removed after being
    hospitalized in days within range(clip_low, clip_high),
    of a truncated_norm(mean, std).
    """
    return sample_truncated_norm(size, clip_low, clip_high, mean, std)


def needs_hospitalization(age):
    """
    Returns if a person needs hospitalization based on their age and data
    extracted from 
    https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf
    """
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
    """
    Returns if a person needs ICU care, given they have been hospitalized,
    based on their age and data extracted from 
    https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf
    """
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
