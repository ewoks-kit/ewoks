def gitlab_pyjobs(pyversion):
    return f"""### Optional jobs for python {pyversion} ###

.test-{pyversion}:
  extends: .test
  image: docker-registry.esrf.fr/dau/ewoks:python_{pyversion}

.test-{pyversion}-win:
  extends: .test-win
  variables:
    PYTHON_VER: "{pyversion}"

.test_sdist-{pyversion}:
  extends: .test_sdist
  image: docker-registry.esrf.fr/dau/ewoks:python_{pyversion}

.test_sdist-{pyversion}-win:
  extends: .test_sdist-win
  variables:
    PYTHON_VER: "{pyversion}"

.test-{pyversion}_glx:
  extends: .test
  image: docker-registry.esrf.fr/dau/ewoks:python_{pyversion}_glx  # libgl1-mesa-glx
  variables:
    QT_QPA_PLATFORM: offscreen

.test-{pyversion}_glx-win:
  extends: .test-win
  variables:
    QT_QPA_PLATFORM: offscreen
    PYTHON_VER: "{pyversion}"

.test_sdist-{pyversion}_glx:
  extends: .test_sdist
  image: docker-registry.esrf.fr/dau/ewoks:python_{pyversion}_glx  # libgl1-mesa-glx
  variables:
    QT_QPA_PLATFORM: offscreen

.test_sdist-{pyversion}_glx-win:
  extends: .test_sdist-win
  variables:
    QT_QPA_PLATFORM: offscreen
    PYTHON_VER: "{pyversion}"
"""


if __name__ == "__main__":
    for pyversion in ("3.6", "3.7", "3.8", "3.9", "3.10"):
        print(gitlab_pyjobs(pyversion))
