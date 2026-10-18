from readme_gen.__main__ import main


def test_generate_writes_icons_and_readme(repo, fake_fetch):
    assert main(["--root", str(repo)], fetch=fake_fetch) == 0

    icons = sorted(p.name for p in (repo / "icons").glob("*.svg"))
    assert icons == ["aws-s3.svg", "c.svg", "cpp.svg", "gtest.svg", "yaml.svg"]
    readme = (repo / "README.md").read_text()
    assert "old table" not in readme
    assert 'src="icons/gtest.svg"' in readme
    assert readme.endswith("<!-- skills:end -->\n\nFooter\n")


def test_generate_removes_stale_icons(repo, fake_fetch):
    (repo / "icons").mkdir()
    (repo / "icons" / "retired.svg").write_text("<svg/>")
    main(["--root", str(repo)], fetch=fake_fetch)
    assert not (repo / "icons" / "retired.svg").exists()


def test_check_passes_when_up_to_date(repo, fake_fetch):
    main(["--root", str(repo)], fetch=fake_fetch)
    assert main(["--root", str(repo), "--check"], fetch=fake_fetch) == 0


def test_check_reports_drift_without_writing(repo, fake_fetch, capsys):
    assert main(["--root", str(repo), "--check"], fetch=fake_fetch) == 1
    assert not (repo / "icons").exists()
    err = capsys.readouterr().err
    assert "out of date: README.md" in err
    assert "out of date: icons/c.svg" in err


def test_check_detects_hand_edited_icon(repo, fake_fetch, capsys):
    main(["--root", str(repo)], fetch=fake_fetch)
    (repo / "icons" / "c.svg").write_text("<svg>edited</svg>")
    assert main(["--root", str(repo), "--check"], fetch=fake_fetch) == 1
    assert "icons/c.svg" in capsys.readouterr().err
