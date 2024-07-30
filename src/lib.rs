use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use unicode_bidi::{BidiInfo, Level};

#[pyfunction]
#[pyo3(signature = (text, base_dir=None, debug=false))]
pub fn get_display_inner(text: &str, base_dir: Option<char>, debug: bool) -> PyResult<String> {
    let level: Option<Level> = match base_dir {
        Some('L') => Some(Level::ltr()),
        Some('R') => Some(Level::rtl()),
        None => None,
        _ => return Err(PyValueError::new_err("base_dir can be 'L', 'R' or None")),
    };
    let bidi_info = BidiInfo::new(text, level);

    if debug {
        return Ok(format!("{bidi_info:#?}"));
    }

    let display: String = bidi_info
        .paragraphs
        .iter()
        .map(|para| {
            let line = para.range.clone();
            bidi_info.reorder_line(para, line)
        })
        .collect();
    Ok(display)
}

#[pyfunction]
pub fn get_base_level_inner(text: &str) -> PyResult<u8> {
    let bidi_info = BidiInfo::new(text, None);
    if bidi_info.paragraphs.is_empty() {
        return Err(PyValueError::new_err("Text contains no paragraphs"));
    }

    Ok(bidi_info.paragraphs[0].level.number())
}

#[pymodule]
fn bidi(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_display_inner, m)?)?;
    m.add_function(wrap_pyfunction!(get_base_level_inner, m)?)?;
    Ok(())
}
