from pytest import mark, raises

from app.schemas.user import UserInsert, UserPatch, check_password


def test_password():
    with raises(ValueError) as error:
        check_password('1234')
    assert 'Password length' in str(error)

    with raises(ValueError) as error:
        check_password('1234123412341234')
    assert 'Variety <' in str(error)

    check_password('new password!!!')


@mark.parametrize('UserClass', [UserInsert, UserPatch])
def test_user_model(UserClass):
    with raises(ValueError):
        UserClass(
            name='abcdef',
            email='invalid.email.com',
            password='valid password!!!',
            is_admin=True,
        )

    with raises(ValueError):
        UserClass(name='abcdef', email='valid@email.com', password='invalid')

    assert UserClass(
        name='abcdef', email='valid@email.com', password='valid password!!!'
    )
